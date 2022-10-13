from email.message import EmailMessage
from flask import current_app
import smtplib

class EmailService:

    def __init__(self) -> None:
        self.email_username = current_app.config["EMAIL_USERNAME"]
        self.email_password = current_app.config["EMAIL_PASSWORD"]
        self.email_host = current_app.config["EMAIL_HOST"]
        self.email_port = current_app.config["EMAIL_PORT"]
        self.email_enabled = current_app.config["EMAIL_ENABLED"]
    
    def send_email(self, recipient_email, subject, message_body):
        if self.email_enabled == "True":
            email = EmailMessage()
            email["From"] = self.email_username
            email["To"] = recipient_email
            email["Subject"] = subject
            email.set_content(message_body)

            smtp = smtplib.SMTP(self.email_host, port=self.email_port)
            smtp.starttls()
            smtp.login(self.email_username, self.email_password)
            smtp.sendmail(self.email_username, recipient_email, email.as_string())
            smtp.quit()