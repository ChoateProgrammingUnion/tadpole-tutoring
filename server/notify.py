import smtplib
import validators
import config
from email.message import EmailMessage


class Email:
    def __init__(self):
        self.smtp = smtplib.SMTP_SSL('smtp.mail.us-east-1.awsapps.com', port=465)
        self.smtp.login(config.EMAIL_USERNAME, config.EMAIL_PASSWORD)

    def send(self, recipient: str, subject = "", msg = "", reminder = True):
        """
        Sends a message
        """
        email = EmailMessage()
        if validators.email(recipient) and subject and msg:
            if reminder:
                msg = msg.rstrip() + "\n\n---\nPlease do not reply to this email. If you have any questions, feel free to email contact@tadpoletutoring.org. We're always happy to chat!"
                # msg = msg.rstrip() + "\n\n---\nPlease do not reply to this email. If you have any questions, feel free to email contact@tadpoletutoring.org. We're always happy to chat!\n\n\nTo stop receiving emails from us, change your notification preferences or let us know at support@tadpoletutoring.org."

            email['Subject'] = subject.rstrip()
            email['From'] = config.EMAIL_USERNAME
            email['To'] = recipient.rstrip()
            email['BCC'] = "tadpoletutoring123@gmail.com"
            email.set_content(msg.rstrip())

            self.smtp.send_message(email)
            # msg = "Subject: " + subject.rstrip() + "\n" + msg.rstrip()
            # print(msg)
            # self.smtp.sendmail(config.EMAIL_USERNAME, recipient, msg)
