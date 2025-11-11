from flask import Flask, request
from twilio.twiml.voice_response import VoiceResponse
from twilio.rest import Client
import os

app = Flask(__name__)

# ---------- MAIN CALL FLOW ----------

@app.route("/voice", methods=["POST"])
def voice():
    """Greets the caller and explains the rules."""
    response = VoiceResponse()
    gather = response.gather(num_digits=1, action="/handle-key", method="POST")

    gather.say("Welcome to Story Line!")
    gather.say("Before you share your story, please follow these rules.")
    gather.say("No inappropriate, violent, or disrespectful stories are allowed.")
    gather.say("If you agree, press 1 to record your story after the beep.")
    gather.say("")
    gather.say("Press 3 to hear the rules again.")

    return str(response)


@app.route("/handle-key", methods=["POST"])
def handle_key():
    """Handles button presses."""
    digits = request.form.get("Digits")
    response = VoiceResponse()

    if digits == "1":
        response.say("Great! After the beep, tell your story. "
                     "Press any key when you are done.")
        response.record(maxLength=120, action="/save-recording",
                        method="POST", finishOnKey="*")

    elif digits == "2":
        response.redirect("/play-story")

    elif digits == "3":
        response.redirect("/voice")

    else:
        response.say("Invalid input. Let's start again.")
        response.redirect("/voice")

    return str(response)


@app.route("/save-recording", methods=["POST"])
def save_recording():
    """Saves the recording and sends you a text with the link."""
    recording_url = request.form.get("RecordingUrl")
    response = VoiceResponse()
    response.say("Thank you for sharing your story! It has been saved. Goodbye.")

    # --- Send SMS to you ---
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    client = Client(account_sid, auth_token)

    from_number = "+18106525229"   # your Twilio phone number
    to_number = "+18104448220"     # your personal phone number

    message = client.messages.create(
        body=f"🎙️ New Story Line recording: {recording_url}",
        from_=from_number,
        to=to_number
    )

    print(f"✅ Text sent! SID: {message.sid}")
    print(f"🎙️ New recording: {recording_url}")

    return str(response)


@app.route("/play-story", methods=["POST"])
def play_story():
    """Plays a past recording (you can add more recordings here)."""
    response = VoiceResponse()

    # Add any recording links you want to play here:
    recordings = [
        "https://api.twilio.com/2010-04-01/Accounts/YOUR_ACCOUNT_SID/Recordings/EXAMPLE1"
    ]

    if not recordings:
        response.say("Sorry, there are no stories available yet.")
    else:
        story = recordings[0]
        response.say("Here's a past story from the Story Line community.")
        response.play(story)
        response.say("Thanks for listening! Goodbye.")

    return str(response)


@app.route("/", methods=["GET"])
def home():
    return "Story Line is running with recording, playback, and SMS alerts!"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
