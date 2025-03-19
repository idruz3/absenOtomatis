import os
import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def download_chromedriver():
    print("Downloading ChromeDriver for packaging...")
    try:
        # Create drivers directory if it doesn't exist
        os.makedirs("drivers", exist_ok=True)
        
        # Download ChromeDriver
        driver_path = ChromeDriverManager().install()
        
        # Copy to drivers directory
        import shutil
        driver_filename = os.path.basename(driver_path)
        shutil.copy2(driver_path, os.path.join("drivers", driver_filename))
        
        print(f"Successfully downloaded ChromeDriver: {driver_filename}")
        print(f"Placed at: {os.path.join(os.getcwd(), 'drivers', driver_filename)}")
        return True
    except Exception as e:
        print(f"Error downloading ChromeDriver: {str(e)}")
        return False

if __name__ == "__main__":
    download_chromedriver()