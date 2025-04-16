from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
service = Service("C:/Users/Long/Desktop/BTL/chromedriver.exe")
options = webdriver.ChromeOptions()
options.add_argument("user-data-dir=C:\\Users\\Long\\AppData\\Local\\Google\\Chrome\\User Data")
options.add_argument("profile-directory=Default")
options.add_argument("--disable-sync")
driver = webdriver.Chrome(service=service, options=options)
driver.get("https://google.com/")
time.sleep(4)
search_box = driver.find_element(By.NAME, "q")
search_box.send_keys("lập trình python")
search_box.send_keys(Keys.ENTER)
driver.quit()
