import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

usernameLMS = input("Please Type your NIM: ")  # Replace with your actual username
passwordLMS = input("Please type your Password: ")  # Replace with your actual password

# Initialize WebDriver
driver = webdriver.Chrome()

# Initialize wait object
wait = WebDriverWait(driver, 10)

# Open the website
driver.get("https://lms.thamrin.ac.id/")


try:
    # Wait for the sign-in button to be clickable and click it
    signIn = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'btn-success')))
    print("Sign-in button found and found.")
    signIn.click()
    
    # Wait for the username field to be clickable and type the username
    login1 = wait.until(EC.element_to_be_clickable((By.ID, 'iduser')))
    login1.send_keys(usernameLMS)
   
    # Wait for the password field to be clickable and type the password
    password1 = wait.until(EC.element_to_be_clickable((By.ID, 'idpass')))
    password1.send_keys(passwordLMS)
    
    # Wait for the continue button to be clickable and click it
    continue1 = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="kt_sign_in_form"]/div[4]/button')))
    continue1.click()
    
    # Check if login was successful by looking for error message
    time.sleep(2)  # Wait for error message if any
    try:
        error_message = driver.find_element(By.ID, 'growls-default')
        print("Login failed: Incorrect username or password")
        driver.quit()
        exit()
    except:
        print("Login successful!")
        # Wait for the virtual class button to be clickable and click it
        vclass = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="kt_content"]/div[2]/strong/strong/div[1]/div[4]/div')))
        vclass.click()
        print("Virtual Class Clicked.")
        pass
    
    # Wait for the class name button
    while True:
        print("1. SI3132 - Pengantar Bisnis dan Manajemen Kelas")
        print("2. KOM3122 - Pemrograman Dasar (C++) Kelas")
        print("3. KOM3121 - Algoritma Pemrograman dan Struktur Data Kelas :A")
        print("4. SI3131 - Konsep Sistem Informasi Kelas")
        print("5. MKK3111 - Bahasa Inggris 1 Kelas")
        print("6. MPK3101 - Pendidikan Pancasila Kelas")
        print("7. MPK3102 - Pendidikan Agama Kelas")
        print("8. MPK3103 - Pendidikan Kewarganegaraan Kelas")
        userinput= input("Enter the class number: ")
        userinput = userinput.lower()
        if userinput == "1":
            kelas1 = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="kt_content"]/div[2]/div[1]/div/div/div[2]/div[2]/div[2]/a')))
            kelas1.click()
            absensi3 = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="kt_content"]/div[2]/div[1]/div/center/button')))
            absensi3.click()
            #absensi1 = wait.until(EC.element_to_be_clickable((By.XPATH, '')))
            #absensi1 = click()
            print("SI3132 - Pengantar Bisnis dan Manajemen Kelas : Clicked.")
            break
        elif userinput == "2":
            kelas2 = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="kt_content"]/div[2]/div[2]/div/div/div[2]/div[2]/div[2]/a')))
            kelas2.click()
            print("KOM3122 - Pemrograman Dasar (C++) Kelas: Clicked")
            absensi3 = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="kt_content"]/div[2]/div[1]/div/center/button')))
            absensi3.click()
            #absensi1 = wait.until(EC.element_to_be_clickable((By.XPATH, '')))
            #absensi1 = click()
            break
        elif userinput == "3":
            kelas3 = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="kt_content"]/div[2]/div[3]/div/div/div[2]/div[2]/div[2]/a')))
            kelas3.click()
            absensi3 = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="kt_content"]/div[2]/div[1]/div/center/button')))
            absensi3.click()
            
            print("Absensi Kelas KOM3121 : Clicked")
            #absensi1 = wait.until(EC.element_to_be_clickable((By.XPATH, '')))
            #absensi1 = click()
            break
        elif userinput == "4":
            kelas4 = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="kt_content"]/div[2]/div[4]/div/div/div[2]/div[2]/div[2]/a')))
            kelas4.click()
            absensi3 = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="kt_content"]/div[2]/div[1]/div/center/button')))
            absensi3.click()
            print("SI3131 - Konsep Sistem Informasi Kelas : Clicked")
            #absensi1 = wait.until(EC.element_to_be_clickable((By.XPATH, '')))
            #absensi1 = click()
            break
        elif userinput == "5":
            kelas5 = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="kt_content"]/div[2]/div[5]/div/div/div[2]/div[2]/div[2]/a')))
            kelas5.click()
            absensi3 = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="kt_content"]/div[2]/div[1]/div/center/button')))
            absensi3.click()
            print("MKK3111 - Bahasa Inggris 1 Kelas : Clicked")
            #absensi1 = wait.until(EC.element_to_be_clickable((By.XPATH, '')))
            #absensi1 = click()
            break
        elif userinput == "6":
            kelas6 = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="kt_content"]/div[2]/div[6]/div/div/div[2]/div[2]/div[2]/a')))
            kelas6.click()
            absensi3 = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="kt_content"]/div[2]/div[1]/div/center/button')))
            absensi3.click()
            print("MPK3101 - Pendidikan Pancasila Kelas : Clicked")
            #absensi1 = wait.until(EC.element_to_be_clickable((By.XPATH, '')))
            #absensi1 = click()
            break
        elif userinput == "7":
            kelas7 = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="kt_content"]/div[2]/div[7]/div/div/div[2]/div[2]/div[2]/a')))
            kelas7.click()
            absensi3 = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="kt_content"]/div[2]/div[1]/div/center/button')))
            absensi3.click()
            print("MPK3102 - Pendidikan Agama Kelas : Clicked")
            #absensi1 = wait.until(EC.element_to_be_clickable((By.XPATH, '')))
            #absensi1 = click()
            break
        elif userinput == "8":
            kelas8 = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="kt_content"]/div[2]/div[8]/div/div/div[2]/div[2]/div[2]/a')))
            kelas8.click()
            absensi3 = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="kt_content"]/div[2]/div[1]/div/center/button')))
            absensi3.click()
            print("MPK3103 - Pendidikan Kewarganegaraan Kelas : Clicked")
            #absensi1 = wait.until(EC.element_to_be_clickable((sBy.XPATH, '')))
            #absensi1 = click()
            break
        else:
            print("Invalid class name.")
        
    # Wait for the element with the class name 'kt-user-card__name' to be present
    #name_element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "kt-user-card__name")))
    # Get the text from the element
    #name_text = name_element.text
    #print("Extracted text:", name_text)
    #link('/vclass/jurnal/KOM3122/A/149')
except Exception as e:
    error_message = driver.find_element(By.ID, 'growls-default')
    print("Login failed: Incorrect username or password")
    driver.quit()
    exit()
    print("An error occurred:", e)
    #time.sleep(5)

finally:
    # Optionally, close the browser
    time.sleep(5)