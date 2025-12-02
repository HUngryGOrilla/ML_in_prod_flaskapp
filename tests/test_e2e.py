import unittest
import time
import random
import string
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class TestE2ESelenium(unittest.TestCase):
    
    def setUp(self):
        service = Service(ChromeDriverManager().install())
        options = webdriver.ChromeOptions()

        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        self.driver = webdriver.Chrome(service=service, options=options)
        self.driver.implicitly_wait(5)
        self.base_url = "http://localhost:5001"
        
        self.wait = WebDriverWait(self.driver, 10)

    def tearDown(self):
        self.driver.quit()

    def generate_username(self):
        return "user_" + ''.join(random.choices(string.ascii_lowercase, k=6))

    def register_and_login(self):
        username = self.generate_username()
        password = "password123"

        self.driver.get(f"{self.base_url}/register")
        self.driver.find_element(By.NAME, "username").send_keys(username)
        self.driver.find_element(By.NAME, "password").send_keys(password)
        self.driver.find_element(By.NAME, "confirm").send_keys(password)
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        self.driver.get(f"{self.base_url}/login")
        self.driver.find_element(By.NAME, "username").send_keys(username)
        self.driver.find_element(By.NAME, "password").send_keys(password)
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        
        self.wait.until(EC.presence_of_element_located((By.LINK_TEXT, "New Task")))
        
        return username

    #Test Login Flow 
    def test_login_flow(self):
        username = self.generate_username()
        password = "securepass"

        self.driver.get(f"{self.base_url}/register")
        self.driver.find_element(By.NAME, "username").send_keys(username)
        self.driver.find_element(By.NAME, "password").send_keys(password)
        self.driver.find_element(By.NAME, "confirm").send_keys(password)
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        self.driver.get(f"{self.base_url}/login")
        self.driver.find_element(By.NAME, "username").send_keys(username)
        self.driver.find_element(By.NAME, "password").send_keys(password)
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        self.wait.until(EC.url_to_be(f"{self.base_url}/"))
        self.assertIn(f"Logged in as {username}", self.driver.page_source)

    #Test Create Task 
    def test_create_task(self):
        self.register_and_login()

        self.driver.find_element(By.LINK_TEXT, "New Task").click()

        task_title = "Selenium Task " + str(random.randint(1, 100))
        self.driver.find_element(By.NAME, "title").send_keys(task_title)
        self.driver.find_element(By.NAME, "description").send_keys("Automated testing")
        
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "task-item")))
        self.assertIn(task_title, self.driver.page_source)

    #Test Toggle Task 
    def test_toggle_task(self):
        self.register_and_login()

        self.driver.find_element(By.LINK_TEXT, "New Task").click()
        self.driver.find_element(By.NAME, "title").send_keys("Task to Toggle")
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        xpath = "//li[contains(., 'Task to Toggle')]//button[contains(text(), 'Complete')]"
        toggle_btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
        toggle_btn.click()

        self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "done")))
        self.assertIn("Done", self.driver.page_source)

if __name__ == "__main__":
    unittest.main()