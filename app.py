from flask import Flask, request, jsonify  # ✅ Required Flask imports
from read_serial import get_temperature    # ✅ Your function that reads Arduino serial

app = Flask(__name__)  # ✅ Create Flask app

@app.route('/')
def home():
    return "Cottage temperature API is running."

@app.route('/alexa', methods=['POST'])
def alexa_handler():
    try:
        req = request.get_json()
        print("Incoming Alexa request:", req)  # Optional: helpful for debugging

        intent = req["request"]["intent"]["name"]

        if intent == "CottageTemperatureIntent":
            temp = get_temperature()

            if temp is None:
                speech = "Sorry, I couldn't read the temperature."
            else:
                speech = f"The temperature in the cottage is {temp:.1f} degrees Celsius."

            return jsonify({
                "version": "1.0",
                "response": {
                    "shouldEndSession": True,
                    "outputSpeech": {
                        "type": "PlainText",
                        "text": speech
                    }
                }
            })

        else:
            return jsonify({
                "version": "1.0",
                "response": {
                    "shouldEndSession": True,
                    "outputSpeech": {
                        "type": "PlainText",
                        "text": "Sorry, I don't understand that request."
                    }
                }
            })

    except Exception as e:
        print("Error:", e)
        return jsonify({
            "version": "1.0",
            "response": {
                "shouldEndSession": True,
                "outputSpeech": {
                    "type": "PlainText",
                    "text": "Something went wrong processing your request."
                }
            }
        })

# ✅ Start the Flask app if this file is run directly
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
