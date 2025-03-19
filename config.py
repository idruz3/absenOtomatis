import webbrowser
from pathlib import Path
from typing import Tuple, Dict
from configparser import ConfigParser

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
                "enabled": "false",  # Disabled by default for new users
                "smtp_server": "smtp.gmail.com",
                "smtp_port": "587",
                "sender_email": "",
                "sender_password": "",
                "recipient_email": ""
            }
            self.config["Settings"] = {
                "check_interval": "3600",  # 1 hour in seconds
                "notification_level": "all"  # all, errors, none
            }
            self.save_config()
            
            # Show a message for first-time users
            self.first_run_message()
    
    def first_run_message(self):
        """Display a message for first-time users"""
        config_path = str(self.config_file)
        
        # Create a simple HTML file with instructions
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
                </ul>
                <p>After editing the configuration, restart the application.</p>
            </body>
            </html>
            """)
        
        # Open the help file
        webbrowser.open(str(help_file))
    
    def save_config(self):
        """Save configuration to file"""
        with open(self.config_file, 'w') as configfile:
            self.config.write(configfile)
    
    def get_credentials(self) -> Tuple[str, str, str]:
        """Get LMS credentials"""
        return (
            self.config["Credentials"]["url"],
            self.config["Credentials"]["username"],
            self.config["Credentials"]["password"]
        )
    
    def get_email_settings(self) -> Dict[str, str]:
        """Get email notification settings"""
        return dict(self.config["Email"])
    
    def get_settings(self) -> Dict[str, str]:
        """Get general settings"""
        return dict(self.config["Settings"])