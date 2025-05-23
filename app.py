from flask import Flask, request, jsonify

app = Flask(__name__)
last_command = ""

@app.route("/device", methods=["GET"])
def get_command():
    global last_command
    cmd = last_command
    last_command = ""  # Clear the command after sending it
    return cmd, 200, {'Content-Type': 'text/plain'}

@app.route("/alexa", methods=["POST"])
def handle_alexa():
    global last_command
    data = request.get_json()
    intent = data['request']['intent']['name']

    intent_to_command = {
        "TurnOnFanIntent": '1',
        "TurnOffFanIntent": '2',
        "TurnOnLightsIntent": '3',
        "TurnOffLightsIntent": '4',
        "TurnOnPurifierIntent": '5',
        "TurnOffPurifierIntent": '6',
        "UnlockDoorIntent": '7',
        "LockDoorIntent": '8'
    }

    if intent in intent_to_command:
        last_command = intent_to_command[intent]
        return jsonify({
            "version": "1.0",
            "response": {
                "outputSpeech": {
                    "type": "PlainText",
                    "text": f"{intent.replace('Intent', '').replace('Turn', '').replace('On', 'On ').replace('Off', 'Off ')} command sent"
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
                    "text": "Unknown command"
                },
                "shouldEndSession": True
            }
        })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
