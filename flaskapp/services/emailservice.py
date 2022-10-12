from email.message import EmailMessage
from flask import current_app
import smtplib

class EmailService:

    def __init__(self) -> None:
        self.email_username = current_app.config["EMAIL_USERNAME"]
        self.email_password = current_app.config["EMAIL_PASSWORD"]
    
    def send_email(self, recipient_email, subject, message_body):
       email = EmailMessage()
       email["From"] = self.email_username
       email["To"] = recipient_email
       email["Subject"] = subject
       email.set_content(message_body)

       smtp = smtplib.SMTP("smtp-mail.outlook.com", port=587)
       smtp.starttls()
       smtp.login(self.email_username, self.email_password)
       smtp.sendmail(self.email_username, recipient_email, email.as_string())
       smtp.quit()