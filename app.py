from flask import Flask, request
from twilio.twiml.voice_response import VoiceResponse
from twilio.rest import Client
import os
import urllib.parse

app = Flask(__name__)

# ---------- MAIN MENU ----------
@app.route("/voice", methods=["POST"])
def voice():
    """Welcome, rules, and main menu."""
    vr = VoiceResponse()
    g = vr.gather(num_digits=1, action="/handle", method="POST")

    g.say("Welcome to Story Line!")
    g.say("Rules: No inappropriate, violent, or disrespectful stories.")
    g.say("If your recording is approved and meets the requirements, "
          "it may be published on the Story Line YouTube channel.")
    g.say("Press 1 to record your story after the beep.")
    g.say("Press 2 to hear the rules again.")

    return str(vr)


@app.route("/handle", methods=["POST"])
def handle():
    """Handle main menu choices."""
    vr = VoiceResponse()
    choice = (request.form.get("Digits") or "").strip()

    if choice == "1":
        vr.say("After the beep, tell your story. Press any key when you are done.")
        vr.record(
            maxLength=120,
            finishOnKey="*",
            trim="trim-silence",
            action="/review",
            method="POST"
        )
        return str(vr)

    if choice == "2":
        vr.redirect("/voice")
        return str(vr)

    vr.say("Invalid input. Let's start again.")
    vr.redirect("/voice")
    return str(vr)


# ---------- REVIEW & CONFIRM ----------
@app.route("/review", methods=["POST"])
def review():
    """Let the caller review their own recording."""
    vr = VoiceResponse()
    rec_url = request.form.get("RecordingUrl")
    rec_sid = request.form.get("RecordingSid")

    if not rec_url:
        vr.say("Sorry, we didn’t receive a recording. Let’s try again.")
        vr.redirect("/voice")
        return str(vr)

    vr.say("Here is your recording.")
    vr.play(rec_url)

    q = urllib.parse.urlencode({"rec_url": rec_url, "rec_sid": rec_sid or ""})
    confirm_action = f"/finalize?{q}"

    g = vr.gather(num_digits=1, action=confirm_action, method="POST")
    g.say("Press 1 to submit your story.")
    g.say("Press 2 to re record.")
    g.say("Press 3 to cancel.")

    return str(vr)


# ---------- FINALIZE ----------
@app.route("/finalize", methods=["POST"])
def finalize():
    """Handle submit, re-record, or cancel."""
    vr = VoiceResponse()
    decision = (request.form.get("Digits") or "").strip()
    rec_url = request.args.get("rec_url") or request.form.get("rec_url")
    rec_sid = request.args.get("rec_sid") or request.form.get("rec_sid")

    if decision == "1":
        # Send SMS alert to you
        try:
            account_sid = os.getenv("TWILIO_ACCOUNT_SID")
            auth_token = os.getenv("TWILIO_AUTH_TOKEN")
            to_number = os.getenv("PERSONAL_PHONE_NUMBER")      # e.g. +18104448220
            from_number = os.getenv("TWILIO_PHONE_NUMBER")       # e.g. +1XXXXXXXXXX
            messaging_sid = os.getenv("TWILIO_MESSAGING_SID")    # optional MGxxxx

            client = Client(account_sid, auth_token)

            if messaging_sid:
                client.messages.create(
                    to=to_number,
                    body=f"🎙️ New Story Line recording submitted: {rec_url}",
                    messaging_service_sid=messaging_sid
                )
            else:
                client.messages.create(
                    to=to_number,
                    from_=from_number,
                    body=f"🎙️ New Story Line recording submitted: {rec_url}"
                )

            print(f"✅ Text sent for recording: {rec_url}")
        except Exception as e:
            print(f"⚠️ SMS error: {e}")

        vr.say("Your story has been submitted.")
        vr.say("If it is approved and meets the requirements, "
               "it may be published on the Story Line YouTube channel.")
        vr.say("Thank you for sharing your story. Goodbye.")
        return str(vr)

    if decision == "2":
        vr.say("Okay, let's try again.")
        vr.redirect("/voice")
        return str(vr)

    if decision == "3":
        vr.say("Cancelled. Goodbye.")
        return str(vr)

    vr.say("Sorry, I didn’t get that.")
    vr.redirect("/review")
    return str(vr)


@app.route("/", methods=["GET"])
def home():
    return "Story Line is running — record → review → submit (with SMS alerts)."


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
