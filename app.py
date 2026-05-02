from flask import Flask, request, jsonify
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

def send_email(subject, body):
    sender = os.environ.get("GMAIL_ADDRESS")
    password = os.environ.get("GMAIL_APP_PASSWORD")
    recipient = os.environ.get("RECIPIENT_EMAIL")

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = recipient

    msg.attach(MIMEText(body, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=25) as server:
        server.login(sender, password)
        server.sendmail(sender, recipient, msg.as_string())

@app.route("/vapi-webhook", methods=["POST"])
def vapi_webhook():
    data = request.json

    # Extract the message type
    message = data.get("message", {})
    msg_type = message.get("type")

    # We only care about end-of-call reports
    if msg_type != "end-of-call-report":
        return jsonify({"status": "ignored"}), 200

    # Pull structured outputs
    analysis = message.get("analysis", {})
    structured = analysis.get("structuredData", {})

    call_summary = analysis.get("summary", "No summary available")
    eval_score = structured.get("Success Evaluation - Numeric Scale", "N/A")
    caller = structured.get("caller_details", {})

    caller_name = caller.get("caller_name", "Unknown")
    callback_number = caller.get("callback_number", "Not provided")
    reason_for_call = caller.get("reason_for_call", "Not provided")
    best_callback_time = caller.get("best_callback_time", "Not specified")

    # Build transcript snippet
    transcript = message.get("transcript", "No transcript available")

    # Format timestamp
    timestamp = datetime.utcnow().strftime("%B %d, %Y at %I:%M %p UTC")

    # Build email
    subject = f"📞 New Call from {caller_name} — {timestamp}"
    body = f"""
    <html><body style="font-family: Arial, sans-serif; max-width: 600px; margin: auto;">
        <h2 style="color: #2c3e50;">📞 Inbound Call Summary</h2>
        <p><strong>Time:</strong> {timestamp}</p>
        <hr>
        <h3>Caller Details</h3>
        <p><strong>Name:</strong> {caller_name}</p>
        <p><strong>Callback Number:</strong> {callback_number}</p>
        <p><strong>Reason for Call:</strong> {reason_for_call}</p>
        <p><strong>Best Callback Time:</strong> {best_callback_time}</p>
        <hr>
        <h3>Call Summary</h3>
        <p>{call_summary}</p>
        <hr>
        <h3>Performance Score</h3>
        <p><strong>{eval_score} / 10</strong></p>
        <hr>
        <h3>Full Transcript</h3>
        <pre style="background:#f4f4f4; padding:10px; border-radius:5px; white-space: pre-wrap;">{transcript}</pre>
    </body></html>
    """

    try:
        send_email(subject, body)
        return jsonify({"status": "email sent"}), 200
    except Exception as e:
        print(f"Email error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/", methods=["GET"])
def health():
    return jsonify({"status": "Alex webhook server is running"}), 200

if __name__ == "__main__":
    app.run(debug=True)
