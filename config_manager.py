# Add this method to your config manager class
def create_default_config(self):
    """Create a default configuration file if none exists"""
    default_config = {
        "credentials": {
            "username": "",
            "password": "",
            "save_credentials": False
        },
        "automation": {
            "check_interval": 3600,
            "start_on_launch": False,
            "headless_mode": True
        },
        "notifications": {
            "email": {
                "enabled": False,
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "sender_email": "",
                "sender_password": "",
                "recipient_email": ""
            },
            "desktop_notifications": True
        },
        "logging": {
            "log_level": "INFO",
            "max_log_files": 5,
            "max_file_size_mb": 5
        },
        "advanced": {
            "browser_timeout": 30,
            "retry_attempts": 3,
            "random_delays": True
        }
    }
    
    try:
        with open(self.config_path, 'w') as f:
            json.dump(default_config, f, indent=4)
        self.logger.info(f"Created default configuration file at {self.config_path}")
        return default_config
    except Exception as e:
        self.logger.error(f"Failed to create default configuration: {str(e)}")
        return {}