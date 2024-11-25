import getpass
import sys
import time
import pwinput
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

def setup_driver():
    """
    Sets up the Chrome WebDriver with specified options.
    Returns:
        WebDriver: The configured WebDriver instance.
    """
    chrome_options = Options()
    chrome_options.add_argument('log-level=3')
    #chrome_options.add_argument("--headless=new")  # Run Chrome in headless mode
    service = Service()  # Update with the path to your chromedriver
    driver = webdriver.Edge(options=chrome_options)  # Initialize the WebDriver with options
    return driver

def login(driver, url, username, password):
    """
    Logs into the specified URL using the provided username and password.
    Args:
        driver (WebDriver): The WebDriver instance used to interact with the web page.
        url (str): The URL of the login page.
        username (str): The username for login.
        password (str): The password for login.
    Returns:
        bool: Returns True if login is successful, otherwise False.
    Raises:
        TimeoutException: If any of the elements are not found within the specified time.
        NoSuchElementException: If the specified elements are not found on the page.
    """
    driver.get(url)
    driver.maximize_window()
    signin_form = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "btn-success")))
    signin_form.click()

    try:
    
        user_field = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "iduser")))
        user_field.send_keys(username)

        password_field = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "idpass")))
        password_field.send_keys(password)

        login_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="kt_sign_in_form"]/div[4]/button')))
        login_button.click()

        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.LINK_TEXT, 'V-Class')))
        return True
    except TimeoutException:
        
        
        return False
    except NoSuchElementException as e:
        print(f"An error occurred: {e}")
        return False

def access_dashboard(driver):
    """
    Accesses the dashboard by interacting with the dropdown menu and retrieves the username.
    Args:
        driver (WebDriver): The WebDriver instance used to interact with the web page.
    Returns:
        bool: Returns False if there is a TimeoutException or NoSuchElementException, otherwise None.
    Raises:
        TimeoutException: If the dropdown or username element is not found within the specified time.
        NoSuchElementException: If the specified elements are not found on the page.
    """
    # Your function implementation here
    try:
        dropdown = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="kt_header"]/div/div/div[2]/div[2]/div[1]/img')))
        dropdown.click()
        time.sleep(2)
        getuserName = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'kt-user-card__name')))
        usernametext = getuserName.text.upper()
        print(f"Welcome, {usernametext}")
    except TimeoutException:
        print("Failed to access the dashboard. quitting...")
        return False
    except NoSuchElementException as e:
        print(f"Element not found! {e}")
        return False
def vClass(driver):
    try:
        vclass = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.LINK_TEXT, 'V-Class')))
        vclass.click()
        #driver.minimize_window()
    except TimeoutException:
        print("Failed to access the virtual class. quitting...")
        return False
    except NoSuchElementException as e:
        print(f"Element not found! {e}")
        return False    

def getClass(driver):
    try:
        class_elements = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'kt-widget__username')))
        for number, class_element in enumerate(class_elements, start=1):
            print(f"Class {number}: {class_element.text}")
        return True, number
    except NoSuchElementException as e:
        print(f"An error occurred: {e}")
        return False, 0

def selectClass(driver, number):
    """
    Attempts to select a class and click an attendance button on a webpage using Selenium WebDriver.
    This function iterates through a list of classes on a webpage, clicks on each class, and checks if a specific 
    attendance button (identified by its XPath) is present. If the button is found, it clicks the button.
    Args:
        driver (WebDriver): The Selenium WebDriver instance used to interact with the webpage.
        number (int): The number of classes to iterate through.
    Returns:
        bool: True if the attendance button is found and clicked at least once, False otherwise.
    Raises:
        Exception: If an unexpected error occurs during execution.
    Notes:
        - The function uses explicit waits to handle dynamic content loading.
        - If the target attendance button is not found after clicking a class, the function navigates back to the previous page 
          and continues with the next class.
        - The function handles TimeoutException and NoSuchElementException for individual elements.
    """
    
    xpath2 = '//*[@id="kt_content"]/div[2]/div[1]/div/center/button'  # Target xpath to find
    button_clicked = False  # Flag to track if the button was clicked at least once

    try:
        for i in range(1, number + 1):
            # First xpath to click
            xpath1 = f'//*[@id="kt_content"]/div[2]/div[{i}]/div/div/div[2]/div[2]'
            try:
                # Click first element
                element1 = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, xpath1))
                )
                element1.click()
                print(f"Mencari tombol absen di kelas nomor {i}, checking absen button...")

                # Check if second xpath exists
                try:
                    element2 = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, xpath2))
                    )
                    print(f"Tombol absen ada di kelas {i}")
                    time.sleep(1)
                    element2.click()
                    print("Clicked absensi button.")
                    button_clicked = True
                except TimeoutException:
                    print(f"Absen button not found, going back...")
                driver.back()
            except TimeoutException:
                print(f"Class element not found for class {i}")
        return button_clicked
    except NoSuchElementException as e:
        print(f"An error occurred: {e}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return False

def main():
    """
    Main function with infinite login attempts until successful or user exits.
    """
    
    #username = sys.argv[1]
    #password = sys.argv[2]
    url = "https://lms.thamrin.ac.id/"
    try:
        
        driver = setup_driver()
        
        if driver is None:
            print("Failed to initialize web driver!")
            return
            
        logged_in = False

        while not logged_in:
            username = input("Please type your NIM (or 'q' to quit): ")
            
            if username.lower() == 'q':
                print("Exiting program...")
                driver.quit()
                return

            password = pwinput.pwinput("Please type your password: ")
            
            try:
                logged_in = login(driver, url, username, password)
                
                if logged_in:
                    access_dashboard(driver)
                    vClass(driver)
                    success, number = getClass(driver)
                    if success:
                        selectClass(driver, number)
                else:
                    print("NIM/Password Salah. Please try again.")
            except Exception as e:
                print(f"An error occurred: {e}")
                print("Please try again.")

        input("Press enter to exit the program \n ")
        print("Exiting program...")
    except Exception as e:
        print(f"Critical error: {e}")

if __name__ == "__main__":
    main()