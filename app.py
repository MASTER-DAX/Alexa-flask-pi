from flask import Flask, request, jsonify

app = Flask(__name__)
latest_command = {"command": None}

@app.route("/alexa-command", methods=["POST"])
def alexa_command():
    data = request.get_json()
    if "command" in data:
        latest_command["command"] = data["command"]
        return jsonify({"status": "Command received"}), 200
    return jsonify({"error": "Invalid format"}), 400

@app.route("/get-command", methods=["GET"])
def get_command():
    return jsonify(latest_command)

@app.route("/clear-command", methods=["POST"])
def clear_command():
    latest_command["command"] = None
    return jsonify({"status": "Command cleared"}), 200
 
if __name__ == "_main_":
    app.run()