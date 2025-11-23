import smtplib
from email.mime.text import MIMEText
from flask import current_app

# -----------------------------------------
# 1. Confirmation Email (after form submit)
# -----------------------------------------
def send_confirmation_email(to_email, user_type):
    body = (
        f"Thanks for submitting your {user_type} profile!\n\n"
        "We’re reviewing your details and will match you as soon as possible.\n\n"
        "- Project Playground Team"
    )

    msg = MIMEText(body)
    msg["Subject"] = f"{user_type.capitalize()} Profile Received"
    msg["From"] = current_app.config["MAIL_USERNAME"]
    msg["To"] = to_email

    send_smtp_email(msg, to_email)


# -----------------------------------------
# 2. Match Email (sent to both sides)
# -----------------------------------------
def send_match_email(receiver_email, partner):
    """
    receiver_email = string email of the person receiving match email
    partner = Founder or Designer object (must have .full_name and .email)
    """

    body = (
        "🎉 You’ve been matched!\n\n"
        "Here are your match details:\n\n"
        f"Name: {partner.full_name}\n"
        f"Email: {partner.email}\n\n"
        "Feel free to reach out and start collaborating!\n\n"
        "- Project Playground"
    )

    msg = MIMEText(body)
    msg["Subject"] = "You Have a New Match 🎉"
    msg["From"] = current_app.config["MAIL_USERNAME"]
    msg["To"] = receiver_email

    send_smtp_email(msg, receiver_email)


# -----------------------------------------
# 3. Shared SMTP Sender (Google App Password)
# -----------------------------------------
def send_smtp_email(message, recipient):
    # Capture the real app object to pass to the thread
    app = current_app._get_current_object()

    def _send_async(app, msg, rcpt):
        with app.app_context():
            try:
                with smtplib.SMTP(
                    app.config["MAIL_SERVER"],
                    app.config["MAIL_PORT"],
                ) as server:
                    server.starttls()
                    server.login(
                        app.config["MAIL_USERNAME"],
                        app.config["MAIL_PASSWORD"],
                    )
                    server.sendmail(
                        msg["From"],
                        [rcpt],
                        msg.as_string(),
                    )
                print(f"✅ Email sent successfully to {rcpt}")
            except Exception as e:
                print("❌ EMAIL ERROR:", e)

    # Start the thread
    from threading import Thread
    Thread(target=_send_async, args=(app, message, recipient)).start()
