from flask import Flask, request, jsonify
import threading

app = Flask(__name__)

# ======================================================
# GLOBAL STATE
# ======================================================
last_command = "0"  # default no command
current_temperature = "not available"

# thread safety (important for Alexa + ESP polling)
lock = threading.Lock()


# ======================================================
# DEVICE POLLING (ESP32 / Arduino gets command here)
# ======================================================
@app.route("/device", methods=["GET"])
def get_command():
    global last_command

    with lock:
        cmd = last_command
        last_command = "0"   # ✅ AUTO RESET (ONE-SHOT COMMAND)

    app.logger.info(f"Sending command to device: {cmd}")
    return cmd


# ======================================================
# TEMPERATURE UPDATE FROM DEVICE
# ======================================================
@app.route("/update_temperature", methods=["POST"])
def update_temperature():
    global current_temperature

    data = request.get_json()
    temperature = data.get("temperature")

    if temperature:
        current_temperature = temperature
        app.logger.info(f"Temperature updated: {temperature}")
        return "Temperature updated", 200

    return "Missing temperature", 400


# ======================================================
# ALEXA HANDLER
# ======================================================
@app.route("/alexa", methods=["POST"])
def handle_alexa():
    global last_command, current_temperature

    data = request.get_json()
    app.logger.info(f"Alexa request data: {data}")

    request_type = data.get('request', {}).get('type', '')

    # --------------------------------------------------
    # Launch
    # --------------------------------------------------
    if request_type == "LaunchRequest":
        return jsonify({
            "version": "1.0",
            "response": {
                "outputSpeech": {
                    "type": "PlainText",
                    "text": "Smart Cottage has activated, you can ask me anything."
                },
                "shouldEndSession": False
            }
        })

    # --------------------------------------------------
    # Intent
    # --------------------------------------------------
    elif request_type == "IntentRequest":
        intent = data['request']['intent']['name']

        # ========== TEMPERATURE ==========
        if intent == "CottageTemperatureIntent":
            return jsonify({
                "version": "1.0",
                "response": {
                    "outputSpeech": {
                        "type": "PlainText",
                        "text": f"The current temperature in the cottage is {current_temperature} degrees."
                    },
                    "shouldEndSession": True
                }
            })

        # ========== INTENT → COMMAND MAP ==========
        intent_to_command = {
            "FrontLightOnIntent": '1',
            "FrontLightOffIntent": '2',
            "BedLightOnIntent": '3',
            "BedLightOffIntent": '4',
            "FrontFanOnIntent": '5',
            "FrontFanOffIntent": '6',
            "BedFanOnIntent": '7',
            "BedFanOffIntent": '8',
            "PurifierOnIntent": '9',
            "PurifierOffIntent": 'A',
            "PrivacyLightsOnIntent": 'B',
            "PrivacyLightsOffIntent": 'C',

            # 🚪 DOOR CONTROL (important for your stepper)
            "FrontDoorUnlockIntent": 'D',  # OPEN → CW
            "FrontDoorLockIntent": 'E',    # CLOSE → CCW
            "BedDoorUnlockIntent": 'F',
            "BedDoorLockIntent": 'G'
        }

        # ========== SEND COMMAND ==========
        if intent in intent_to_command:
            with lock:
                last_command = intent_to_command[intent]

            app.logger.info(f"Alexa intent '{intent}' -> command '{last_command}'")

            return jsonify({
                "version": "1.0",
                "response": {
                    "outputSpeech": {
                        "type": "PlainText",
                        "text": "Command granted."
                    },
                    "shouldEndSession": True
                }
            })

        else:
            return jsonify({
                "version": "1.0",
                "response": {
                    "outputSpeech": {
                        "type": "PlainText",
                        "text": "Unknown command."
                    },
                    "shouldEndSession": True
                }
            })

    # --------------------------------------------------
    # Session End
    # --------------------------------------------------
    elif request_type == "SessionEndedRequest":
        return jsonify({})

    else:
        return jsonify({
            "version": "1.0",
            "response": {
                "outputSpeech": {
                    "type": "PlainText",
                    "text": "Sorry, I couldn't understand the request type."
                },
                "shouldEndSession": True
            }
        })


# ======================================================
# MANUAL RESET (optional)
# ======================================================
@app.route("/reset_command", methods=["POST"])
def reset_command():
    global last_command

    with lock:
        last_command = "0"

    return "Command reset", 200


# ======================================================
# RUN SERVER
# ======================================================
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
