from flask import Flask, request, jsonify

app = Flask(__name__)

# Simulated temperature sensor function
def get_temperature():
    # Replace this with actual sensor reading from Raspberry Pi
    return 21.7

@app.route('/alexa', methods=['POST'])
def alexa_handler():
    try:
        req = request.get_json()
        print("Incoming Alexa request:", req)

        # LaunchRequest — when user says "open Cottage Monitor"
        if req["request"]["type"] == "LaunchRequest":
            speech = "Welcome to the Cottage Monitor. You can ask for the temperature."

        # IntentRequest — when user says something like "what's the temperature"
        elif req["request"]["type"] == "IntentRequest":
            intent_name = req["request"]["intent"]["name"]

            if intent_name == "CottageTemperatureIntent":
                temp = get_temperature()
                if temp is not None:
                    speech = f"The temperature in the cottage is {temp:.1f} degrees Celsius."
                else:
                    speech = "Sorry, I couldn't read the temperature."
            else:
                speech = "Sorry, I don't understand that request."

        # Catch-all for other request types
        else:
            speech = "Sorry, I couldn't process that request."

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
