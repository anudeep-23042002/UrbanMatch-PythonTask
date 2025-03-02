import smtplib
import token_util
import os
from email.mime.text import MIMEText

SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = os.getenv("SMTP_PORT")
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

def send_verification_email(to_email: str):
    token = token_util.generate_jwt_token(to_email)
    #url of the app (used local host)
    verification_link = f"http://127.0.0.1:8000/verify-email/{token}"
    message = f"Click the link to verify your email: {verification_link}"
    
    msg = MIMEText(message)
    msg["Subject"] = "Verify Your Email For the Account of Match Making site"
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = to_email

    try:
        server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, to_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print("Error sending email:", e)
        return False
