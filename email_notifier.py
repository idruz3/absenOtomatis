import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

from config import Config
from logging_utils import Logger

class EmailNotifier:
    """Class for sending email notifications"""
    
    def __init__(self, config: Config, logger: Logger):
        self.config = config
        self.logger = logger
        self.email_settings = config.get_email_settings()
        self.enabled = self.email_settings.get("enabled", "false").lower() == "true"
    
    def send_notification(self, subject: str, message: str, category: str = "info") -> bool:
        """Send email notification"""
        if not self.enabled:
            self.logger.warning("Email notifications are disabled in config")
            return False
            
        # Check notification level
        notification_level = self.config.get_settings().get("notification_level", "all").lower()
        if notification_level == "none" or (notification_level == "errors" and category != "error"):
            self.logger.warning(f"Notification level '{notification_level}' prevented this {category} email")
            return False
            
        try:
            # Set up email
            msg = MIMEMultipart()
            msg["From"] = self.email_settings["sender_email"]
            msg["To"] = self.email_settings["recipient_email"]
            msg["Subject"] = f"LMS Automation: {subject}"
            
            # Add timestamp and category to message
            email_body = f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            email_body += f"Category: {category.upper()}\n\n"
            email_body += message
            
            msg.attach(MIMEText(email_body, "plain"))
            
            # Connect to server and send email
            self.logger.info(f"Connecting to SMTP server: {self.email_settings['smtp_server']}:{self.email_settings['smtp_port']}")
            with smtplib.SMTP(self.email_settings["smtp_server"], int(self.email_settings["smtp_port"])) as server:
                server.starttls()
                self.logger.info(f"Logging in as {self.email_settings['sender_email']}")
                server.login(self.email_settings["sender_email"], self.email_settings["sender_password"])
                server.send_message(msg)
                
            self.logger.info(f"Email notification sent: {subject}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send email notification: {str(e)}")
            return False