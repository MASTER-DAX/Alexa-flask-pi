from flask import Flask, request, jsonify

app = Flask(__name__)
last_command = ""

@app.route("/device", methods=["GET"])
def get_command():
    global last_command
    return last_command

@app.route("/alexa", methods=["POST"])
def handle_alexa():
    global last_command
    data = request.get_json()
    app.logger.info(f"Alexa request data: {data}")

    request_type = data.get('request', {}).get('type', '')

    if request_type == "LaunchRequest":
        return jsonify({
            "version": "1.0",
            "response": {
                "outputSpeech": {
                    "type": "PlainText",
                    "text": "Welcome to Smart Cottage, You can ask me anything."
                },
                "shouldEndSession": False
            }
        })

    elif request_type == "IntentRequest":
        try:
            intent = data['request']['intent']['name']
        except (KeyError, TypeError):
            return jsonify({
                "version": "1.0",
                "response": {
                    "outputSpeech": {
                        "type": "PlainText",
                        "text": "Sorry, I couldn't understand the command."
                    },
                    "shouldEndSession": True
                }
            })

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

    elif request_type == "SessionEndedRequest":
        # Optionally handle session end here
        return jsonify({})

    else:
        return jsonify({
            "version": "1.0",
            "response": {
                "outputSpeech": {
                    "type": "PlainText",
                    "text": "Sorry, I couldn't understand the request type."
                },
                "shouldEndSession": True
            }
        })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
