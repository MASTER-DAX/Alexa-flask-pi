from flask import Flask, request, jsonify
from read_serial import get_temperature

app = Flask(__name__)

@app.route('/')
def home():
    return "Cottage temperature API is running."

@app.route('/alexa', methods=['POST'])
def alexa_handler():
    req = request.get_json()
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
    
    return jsonify({})
