import sys
from pathlib import Path
from configparser import ConfigParser
import webbrowser

class Config:
    """Configuration management class"""

    def __init__(self):
        self.config_file = Path.home() / "lms_automation_config.ini"
        self.config = ConfigParser()
        self.load_config()

    def load_config(self):
        """Load configuration from file or create default"""
        if self.config_file.exists():
            self.config.read(self.config_file)
        else:
            # Create default configuration with empty credentials
            self.config["Credentials"] = {
                "url": "https://lms.thamrin.ac.id/",
                "username": "",
                "password": ""
            }
            self.config["Email"] = {
                "enabled": "false",
                "smtp_server": "smtp.gmail.com",
                "smtp_port": "587",
                "sender_email": "",
                "sender_password": "",
                "recipient_email": ""
            }
            self.config["WhatsApp"] = {
                "enabled": "false",
                "recipient_number": ""
            }
            self.config["Settings"] = {
                "check_interval": "3600",
                "notification_level": "all"
            }
            self.save_config()
            self.first_run_message()
            sys.exit("Please configure the INI file and restart the application.")

    def first_run_message(self):
        """Display a message for first-time users"""
        config_path = str(self.config_file)
        help_file = Path.home() / "lms_automation_setup.html"
        
        with open(help_file, 'w') as f:
            f.write(f"""
            <html>
            <body>
                <h1>LMS Attendance Automation - First Run Setup</h1>
                <p>Welcome to LMS Attendance Automation! Before using the application, you need to configure your credentials.</p>
                <p>Please edit the configuration file at: <code>{config_path}</code></p>
                <h2>Required Settings:</h2>
                <ul>
                    <li>Your LMS username and password</li>
                    <li>Your email settings (if you want email notifications)</li>
                    <li>Your WhatsApp settings (if you want WhatsApp notifications)</li>
                </ul>
                <p>After editing the configuration, restart the application.</p>
            </body>
            </html>
            """)

        webbrowser.open(str(help_file))
        webbrowser.open(config_path)

    def save_config(self):
        """Save configuration to file"""
        with open(self.config_file, 'w') as configfile:
            self.config.write(configfile)

    def get_credentials(self):
        """Get LMS credentials"""
        return (
            self.config["Credentials"]["url"],
            self.config["Credentials"]["username"],
            self.config["Credentials"]["password"]
        )

    def get_email_settings(self):
        """Get email notification settings"""
        return dict(self.config["Email"])

    def get_whatsapp_settings(self):
        """Get WhatsApp notification settings"""
        return dict(self.config["WhatsApp"])

    def get_settings(self):
        """Get general settings"""
        return dict(self.config["Settings"])