import getpass
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
    signin_form = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "btn-success")))
    signin_form.click()
    driver.maximize_window()

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
        print("Login failed: Incorrect username or password")
        
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
    xpath2 = '//*[@id="kt_content"]/div[2]/div[1]/div/center/button'  # Target xpath to find
    
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
                #print(f"Clicked first element {i}, checking for target xpath...")

                # Check if second xpath exists
                try:
                    element2 = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, xpath2))
                    )
                    #print(f"Target xpath found after clicking element {i}")
                    element2.click()
                    print("Clicked absensi button")
                    return True
                except TimeoutException:
                    #print(f"Target xpath not found, going back...")
                    driver.back()
                    time.sleep(2)  # Wait for page to load
                    continue

            except (TimeoutException, NoSuchElementException) as e:
                print(f"Error with element {i}: {e}")
                continue

        print("Button absensi not found")
        return False

    except Exception as e:
        print(f"Unexpected error: {e}")
        return False
    
       
            
         
def main():
    """
    Main function with infinite login attempts until successful or user exits.
    """
    print("Starting attendance automation...")  # Debug print
    
    url = "https://lms.thamrin.ac.id/"
    try:
        print("Setting up web driver...")  # Debug print
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
                    print("Invalid credentials. Please try again.")
            except Exception as e:
                print(f"An error occurred: {e}")
                print("Please try again.")

        #driver.quit()
    except Exception as e:
        print(f"Critical error: {e}")

if __name__ == "__main__":
    main()