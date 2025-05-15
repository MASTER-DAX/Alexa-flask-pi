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

    # Simple parser (optional: enhance this)
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
    # Implement if needed: return a command string to ESP
    return "", 200

@app.route("/alexa", methods=["POST"])
def alexa_skill():
    req = request.get_json()
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

    return jsonify({
        "version": "1.0",
        "response": {
            "shouldEndSession": True,
            "outputSpeech": {
                "type": "PlainText",
                "text": "Sorry, I didn't understand that."
            }
        }
    })
