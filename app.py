from flask import Flask, request, jsonify

app = Flask(__name__)

# Store the latest sensor data received from ESP32
latest_data = {
    "temperature": None,
    "gas": None,
    "fan": "OFF",
    "purifier": "OFF"
}

@app.route("/esp", methods=["POST"])
def esp_post():
    data = request.get_json()
    message = data.get("message", "")

    # Simple parser
    if "Temperature" in message:
        parts = message.split(",")
        for part in parts:
            if "Temperature" in part:
                latest_data["temperature"] = part.split(":")[1].strip().replace("C", "")
            if "Gas Level" in part:
                latest_data["gas"] = part.split(":")[1].strip()
    elif "FAN:" in message:
        latest_data["fan"] = "ON" if "ON" in message else "OFF"
    elif "GAS:HIGH" in message:
        latest_data["purifier"] = "ON"
    elif "Purifier OFF" in message:
        latest_data["purifier"] = "OFF"

    return jsonify({"status": "ok"})

@app.route("/command", methods=["GET"])
def get_command():
    # Optional: return any command to be received by ESP
    return "", 200

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
                        "text": "Welcome to Cottage Monitor. You can ask for the temperature."
                    }
                }
            })

        elif req_type == "IntentRequest":
            intent_name = req["request"]["intent"]["name"]

            if intent_name == "CottageTemperatureIntent":
                temp = latest_data["temperature"]
                if temp:
                    response_text = f"The current temperature is {temp} degrees Celsius."
                else:
                    response_text = "Sorry, I couldn't get the temperature right now."

                return jsonify({
                    "version": "1.0",
                    "response": {
                        "shouldEndSession": True,
                        "outputSpeech": {
                            "type": "PlainText",
                            "text": response_text
                        }
                    }
                })

        # Fallback for unknown intents
        return jsonify({
            "version": "1.0",
            "response": {
                "shouldEndSession": True,
                "outputSpeech": {
                    "type": "PlainText",
                    "text": "Sorry, I didn't understand that request."
                }
            }
        })

    except Exception as e:
        print(f"Error handling Alexa request: {e}")
        return jsonify({
            "version": "1.0",
            "response": {
                "shouldEndSession": True,
                "outputSpeech": {
                    "type": "PlainText",
                    "text": "Something went wrong on the server."
                }
            }
        })

if __name__ == "__main__":
    app.run(debug=True)
