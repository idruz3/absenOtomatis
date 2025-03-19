import os
import time
import random
from typing import Optional

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from logging_utils import Logger

class WebDriverManager:
    """Class for managing the WebDriver"""
    
    def __init__(self, logger: Logger):
        self.logger = logger
        self.driver = None
        self.driver_options = self._create_options()
    
    def _create_options(self) -> Options:
        """Create optimized Chrome options - only called once"""
        chrome_options = Options()
        chrome_options.add_argument('log-level=3')  # Suppress browser logs
        chrome_options.add_argument("--headless=new")  # Run in headless mode
        
        # Add additional arguments to improve stability and performance
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-software-rasterizer")
        chrome_options.add_argument("--disable-features=IsolateOrigins,site-per-process")
        chrome_options.add_argument("--blink-settings=imagesEnabled=false")  # Disable images
        
        return chrome_options
    
    def setup_driver(self) -> Optional[webdriver.Chrome]:
        """Initialize Chrome webdriver with previously created options"""
        try:
            # Create a unique user data directory
            unique_id = f"{int(time.time())}_{random.randint(10000, 99999)}"
            temp_dir = os.path.join(os.environ.get('TEMP', '/tmp'), f'chrome_user_data_{unique_id}')
            os.makedirs(temp_dir, exist_ok=True)
            
            # Apply unique user directory to existing options
            options = self.driver_options
            options.add_argument(f"--user-data-dir={temp_dir}")
            
            # Use ChromeDriverManager for automatic driver management
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
            return self.driver
        except Exception as e:
            self.logger.error(f"Failed to initialize WebDriver: {e}")
            return None
    
    def close_driver(self) -> None:
        """Close the WebDriver safely"""
        try:
            if self.driver:
                self.driver.quit()
                self.driver = None
        except Exception as e:
            self.logger.error(f"Error closing WebDriver: {e}")