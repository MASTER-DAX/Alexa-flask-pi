from flask import Flask, request, jsonify

app = Flask(__name__)

# Dummy temperature reading function
def get_temperature():
    try:
        # Replace this with real sensor reading logic (e.g., from DHT22)
        return 22.5  # Example static temperature
    except Exception as e:
        print("Error getting temperature:", e)
        return None

@app.route('/alexa', methods=['POST'])
def alexa_handler():
    try:
        req = request.get_json()
        print("Incoming Alexa request:", req)

        # Check the type of request
        if req["request"]["type"] == "IntentRequest":
            intent = req["request"]["intent"]["name"]

            if intent == "CottageTemperatureIntent":
                temp = get_temperature()

                if temp is None:
                    speech = "Sorry, I couldn't read the temperature."
                else:
                    speech = f"The temperature in the cottage is {temp:.1f} degrees Celsius."
            else:
                speech = "Sorry, I don't understand that request."

        elif req["request"]["type"] == "LaunchRequest":
            speech = "Welcome to the Cottage Monitor. You can ask for the temperature."

        else:
            speech = "Thank you. Goodbye!"

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
    app.run(debug=True, port=5000)
