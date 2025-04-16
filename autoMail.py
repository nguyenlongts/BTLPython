from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service

def send_email(to_email, subject, body):
    try:
        service = Service("C:/Users/Long/Desktop/BTL/chromedriver.exe")

        options = webdriver.ChromeOptions()
        options.add_argument("user-data-dir=C:\\Users\\Long\\AppData\\Local\\Google\\Chrome\\User Data")
        options.add_argument("profile-directory=Default")
        options.add_argument("--disable-sync")
        driver = webdriver.Chrome(service=service, options=options)
        driver.get("https://mail.google.com/")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Compose')]")))
        compose_button = driver.find_element(By.XPATH, "//div[contains(text(), 'Compose')]")
        compose_button.click()
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='dialog']")))
        to_field = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//input[@aria-label='To recipients']"))
        )
        to_field.send_keys(to_email)
        time.sleep(5)

        subject_field = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='subjectbox'], input[placeholder='Subject']"))
        )
        subject_field.send_keys(subject)
        time.sleep(5)

        body_field = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "div[role='textbox'][aria-label='Message Body'], div[contenteditable='true'][aria-label='Message Body']"))
        )
        body_field.send_keys(body)
        time.sleep(5)

        send_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "div[role='button'][aria-label*='Send']"))
        )
        send_button.click()

        print("✅ Email đã được gửi thành công!")

        time.sleep(3)
        return True
    except Exception as e:
        print(f" Lỗi khi gửi email: {e}")
        return False
    finally:
        driver.quit()
