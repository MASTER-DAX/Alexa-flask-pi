from flask import Flask, request, jsonify
from datetime import datetime, timedelta

app = Flask(__name__)

# Store the latest sensor data received from ESP32
latest_data = {
    "temperature": None,
    "gas": None,
    "fan": "OFF",
    "purifier": "OFF",
    "last_updated": None
}

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
    elif "GAS:HIGH" in message:
        latest_data["purifier"] = "ON"
    elif "Purifier OFF" in message:
        latest_data["purifier"] = "OFF"

    return jsonify({"status": "ok"})

@app.route("/command", methods=["GET"])
def get_command():
    return "", 200

@app.route("/smarthome", methods=["POST"])
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
                last_updated = latest_data["last_updated"]

                # Check if data is recent (within last 30 seconds)
                if temp and last_updated and datetime.utcnow() - last_updated < timedelta(seconds=30):
                    response_text = f"The current temperature is {temp} degrees Celsius."
                else:
                    response_text = "Sorry, I couldn't get the current temperature. Please try again shortly."

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
