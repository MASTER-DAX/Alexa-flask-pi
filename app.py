from flask import Flask, request, jsonify

app = Flask(__name__)
last_command = ""
current_temperature = "not available"

@app.route("/device", methods=["GET"])
def get_command():
    global last_command
    return last_command

@app.route("/update_temperature", methods=["POST"])
def update_temperature():
    global current_temperature
    data = request.get_json()
    temperature = data.get("temperature")
    if temperature:
        current_temperature = temperature
        return "Temperature updated", 200
    return "Missing temperature", 400

@app.route("/alexa", methods=["POST"])
def handle_alexa():
    global last_command, current_temperature
    data = request.get_json()
    app.logger.info(f"Alexa request data: {data}")

    request_type = data.get('request', {}).get('type', '')

    if request_type == "LaunchRequest":
        return jsonify({
            "version": "1.0",
            "response": {
                "outputSpeech": {
                    "type": "PlainText",
                    "text": "Smart Cottage has activated, You can ask me anything"
                },
                "shouldEndSession": False
            }
        })

    elif request_type == "IntentRequest":
        intent = data['request']['intent']['name']

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
    "FrontDoorUnlockIntent": 'D',
    "FrontDoorLockIntent": 'E',
    "BedDoorUnlockIntent": 'F',
    "BedDoorLockIntent": 'G'
}


        if intent in intent_to_command:
            last_command = intent_to_command[intent]
            return jsonify({
                "version": "1.0",
                "response": {
                    "outputSpeech": {
                        "type": "PlainText",
                        "text": "Command granted"
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

@app.route("/reset_command", methods=["POST"])
def reset_command():
    global last_command
    last_command = "0"  # default = no command
    return "Command reset", 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
