from flask import Flask, request, send_file
from twilio.twiml.voice_response import VoiceResponse
import os

app = Flask(__name__)

# Step 1: Welcome + Rules
@app.route("/voice", methods=["POST"])
def voice():
    response = VoiceResponse()
    gather = response.gather(
        num_digits=1,
        action="/handle-key",
        method="POST"
    )
    gather.say("Welcome to Story Line! Before you share your story, please remember these rules.")
    gather.say("No inappropriate, violent, or disrespectful stories are allowed.")
    gather.say("If you understand and agree, press 1 to begin recording your story after the beep.")
    gather.say("Press 2 to hear these rules again.")
    return str(response)

# Step 2: Handle button press
@app.route("/handle-key", methods=["POST"])
def handle_key():
    response = VoiceResponse()
    digits = request.form.get("Digits")

    if digits == "1":
        response.say("Great! After the beep, tell your story. Press any key when you are done.")
        response.record(maxLength=120, action="/save-recording", method="POST", finishOnKey="*")
    elif digits == "2":
        response.redirect("/voice")
    else:
        response.say("Invalid input. Let's start again.")
        response.redirect("/voice")
    return str(response)

# Step 3: Save the recording
@app.route("/save-recording", methods=["POST"])
def save_recording():
    recording_url = request.form.get("RecordingUrl")
    response = VoiceResponse()
    response.say("Thank you for sharing your story! It has been saved. Goodbye.")
    print(f"🎙️ New recording: {recording_url}")
    return str(response)

@app.route("/", methods=["GET"])
def home():
    return "Story Line is running with recording support!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
