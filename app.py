from flask import Flask, request, jsonify
from read_serial import get_temperature  # use the real serial-reading function

import traceback

app = Flask(__name__)

@app.route('/alexa', methods=['POST'])
def alexa_handler():
    try:
        req = request.get_json()
        print("Incoming Alexa request:", req)

        request_type = req.get("request", {}).get("type")

        if request_type == "IntentRequest":
            intent_name = req["request"]["intent"]["name"]

            if intent_name == "CottageTemperatureIntent":
                temp = get_temperature()
                if temp is None:
                    speech = "Sorry, I couldn't read the temperature from the cottage sensor."
                else:
                    speech = f"The temperature in the cottage is {temp:.1f} degrees Celsius."
            else:
                speech = "Sorry, I don't understand that request."

        elif request_type == "LaunchRequest":
            speech = "Welcome to the Cottage Monitor. You can ask me for the temperature."

        else:
            speech = "Sorry, I couldn't process that request type."

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
        traceback.print_exc()
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
