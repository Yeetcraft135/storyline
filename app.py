from flask import Flask, request
from twilio.twiml.voice_response import VoiceResponse

app = Flask(__name__)

@app.route("/voice", methods=["POST"])
def voice():
    vr = VoiceResponse()
    vr.say("Welcome to Story Line. The connection works!")
    return str(vr)

if __name__ == "__main__":
    app.run(port=5000, debug=True)
