from email.message import EmailMessage
import smtplib

class EmailService:

    def __init__(self) -> None:
        self.email_username = "graciao@uninorte.edu.co"
        self.email_password = "MinTic2.." # TODO: retrieve from configuration file.
    
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