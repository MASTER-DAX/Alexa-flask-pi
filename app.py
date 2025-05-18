from flask import Flask, request, jsonify
from datetime import datetime, timedelta

app = Flask(__name__)

# Store the latest sensor and device state
latest_data = {
    "temperature": None,
    "gas": None,
    "fan": "OFF",
    "lights": "OFF",
    "purifier": "OFF",
    "last_updated": None
}

# Store the latest command from Alexa
latest_command = None

@app.route("/esp", methods=["POST"])
def esp_post():
    data = request.get_json()
    message = data.get("message", "")

    if "Temperature" in message:
        parts = message.split(",")
        for part in parts:
            if "Temperature" in part:
                latest_data["temperature"] = part.split(":")[1].strip().replace("C", "")
            if "Gas Level" in part:
                latest_data["gas"] = part.split(":")[1].strip()
        latest_data["last_updated"] = datetime.utcnow()

    elif "FAN:" in message:
        latest_data["fan"] = "ON" if "ON" in message else "OFF"
    elif "LIGHTS:" in message:
        latest_data["lights"] = "ON" if "ON" in message else "OFF"
    elif "PURIFIER:" in message:
        latest_data["purifier"] = "ON" if "ON" in message else "OFF"

    return jsonify({"status": "ok"})


@app.route("/command", methods=["GET"])
def get_command():
    global latest_command
    if latest_command:
        cmd = latest_command
        latest_command = None  # Clear after reading
        print(f"[Command sent to ESP32]: {cmd}")
        return cmd
    else:
        return "", 204  # No content


@app.route("/alexa", methods=["POST"])
def alexa_skill():
    req = request.get_json()

    try:
        req_type = req["request"]["type"]

        if req_type == "LaunchRequest":
            return jsonify({
                "version": "1.0",
                "response": {
                    "shouldEndSession": False,
                    "outputSpeech": {
                        "type": "PlainText",
                        "text": "Welcome to Cottage Monitor. You can say turn on the fan, lights, or purifier."
                    }
                }
            })

        elif req_type == "IntentRequest":
            intent = req["request"]["intent"]["name"]

            if intent == "CottageTemperatureIntent":
                temp = latest_data["temperature"]
                last_updated = latest_data["last_updated"]
                if temp and last_updated and datetime.utcnow() - last_updated < timedelta(seconds=30):
                    response_text = f"The current temperature is {temp} degrees Celsius."
                else:
                    response_text = "Sorry, I couldn't get the current temperature. Please try again shortly."
                return simple_response(response_text)

            # Device control intents
            elif intent == "TurnOnFanIntent":
                send_command("FAN:ON")
                latest_data["fan"] = "ON"
                return simple_response("Fan has been turned on.")

            elif intent == "TurnOffFanIntent":
                send_command("FAN:OFF")
                latest_data["fan"] = "OFF"
                return simple_response("Fan has been turned off.")

            elif intent == "TurnOnLightsIntent":
                send_command("LIGHTS:ON")
                latest_data["lights"] = "ON"
                return simple_response("Lights have been turned on.")

            elif intent == "TurnOffLightsIntent":
                send_command("LIGHTS:OFF")
                latest_data["lights"] = "OFF"
                return simple_response("Lights have been turned off.")

            elif intent == "TurnOnPurifierIntent":
                send_command("PURIFIER:ON")
                latest_data["purifier"] = "ON"
                return simple_response("Purifier has been turned on.")

            elif intent == "TurnOffPurifierIntent":
                send_command("PURIFIER:OFF")
                latest_data["purifier"] = "OFF"
                return simple_response("Purifier has been turned off.")

        return simple_response("Sorry, I didn't understand that request.")

    except Exception as e:
        print(f"Error: {e}")
        return simple_response("Something went wrong on the server.")


def send_command(cmd):
    global latest_command
    latest_command = cmd
    print(f"[Command stored for ESP32]: {cmd}")


def simple_response(text):
    return jsonify({
        "version": "1.0",
        "response": {
            "shouldEndSession": True,
            "outputSpeech": {
                "type": "PlainText",
                "text": text
            }
        }
    })


if __name__ == "__main__":
    app.run(debug=True)
