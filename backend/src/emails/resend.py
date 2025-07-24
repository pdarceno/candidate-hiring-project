import os
import resend

resend.api_key = os.environ["RESEND_API_KEY"]

address = os.environ.get("RESEND_EMAIL_ADDRESS")

def send_enhancement_email(subject: str, html_content: str):
    """Send an email with the enhancement result."""
    params: resend.Emails.SendParams = {
        "from": "Acme <onboarding@resend.dev>",
        "to": [address],
        "subject": subject,
        "html": html_content,
    }

    email = resend.Emails.send(params)
    return email