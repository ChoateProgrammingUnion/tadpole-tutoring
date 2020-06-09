import smtplib
import validators
import config
from email.message import EmailMessage
from utils.log import log_info


class Email:
    def __init__(self):
        pass
        
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

    def send2(recipient,subject,msg="",reminder=True): # V2 not really sure why V1 doesn't work
        email = EmailMessage() # create the email message object    
        if reminder: #detect type of email that was requested
            email.set_content("This is a reminder for your tutoring session")
            email["Subject"] = "Tutoring Reminder"
            email["From"] = "noreply@tadpoletutoring.org"
            email["To"] = recipient
            email["BCC"] = "tadpoletutoring123@gmail.com" 
        else:
            email.set_content(msg) 
            email["Subject"] = subject
            email["From"] = "noreply@tadpoletutoring.org"
            email["To"] = recipient
            email["BCC"] = "tadpoletutoring123@gmail.com"
        try:
            mail = smtplib.SMTP_SSL('smtp.mail.us-east-1.awsapps.com', port=465)
        except Exception as e:
            log_info(e)
            return "login error"
        try:
            mail.login(config.EMAIL_USERNAME, config.EMAIL_PASSWORD)
        except Exception as e:
            log_info(e)
            return "wrong password/username"
        try:
            mail.send_message(email)
        except Exception as e:
            log_info(e)
            return "send mail error"
        return True
        mail.quit()

