from flask import Flask, request
from twilio.twiml.voice_response import VoiceResponse

app = Flask(__name__)

@app.route("/voice", methods=["POST"])
def voice():
    vr = VoiceResponse()
    vr.say("Welcome to Story Line. The connection works!")
    return str(vr)

@app.route("/", methods=["GET"])
def home():
    return "Story Line is running!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
