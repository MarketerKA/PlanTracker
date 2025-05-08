from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import UnexpectedAlertPresentException, NoAlertPresentException
import sys
import os
import time

# Add the parent directory to the path to enable imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from conftest import BASE_URL

class LoginPage:
    # URL
    URL = f"{BASE_URL}/login"
    
    # Locators
    EMAIL_FIELD = (By.CSS_SELECTOR, "input[type='email']")
    PASSWORD_FIELD = (By.CSS_SELECTOR, "input[placeholder='Enter password']")
    LOGIN_BUTTON = (By.CSS_SELECTOR, "button[type='submit']")
    REGISTER_LINK = (By.CSS_SELECTOR, "button[type='button']")
    SERVER_ERROR = (By.CSS_SELECTOR, ".serverError")
    
    # Error message locators
    EMAIL_ERROR = (By.XPATH, "//label[text()='Email']/following-sibling::div/following-sibling::div[contains(@class, 'errorMessage')]")
    PASSWORD_ERROR = (By.XPATH, "//label[text()='Password']/following-sibling::div/following-sibling::div[contains(@class, 'errorMessage')]")
    
    def __init__(self, driver: WebDriver):
        self.driver = driver
        self.alert_text = None
        
    def navigate(self):
        """Navigate to the login page"""
        self.driver.get(self.URL)
        return self
        
    def set_email(self, email: str):
        """Set the email input field"""
        email_field = self.driver.find_element(*self.EMAIL_FIELD)
        email_field.clear()
        email_field.send_keys(email)
        return self
        
    def set_password(self, password: str):
        """Set the password input field"""
        password_field = self.driver.find_element(*self.PASSWORD_FIELD)
        password_field.clear()
        password_field.send_keys(password)
        return self
        
    def click_login(self):
        """Click the login button and handle any alerts"""
        try:
            self.driver.find_element(*self.LOGIN_BUTTON).click()
            # Short pause to allow for form submission or alert to appear
            time.sleep(1)
        except UnexpectedAlertPresentException as e:
            # Store the alert text for later assertions
            self.alert_text = e.alert_text
            print(f"Alert captured: {self.alert_text}")
            
        # Try to handle any alert that might be present
        try:
            alert = self.driver.switch_to.alert
            self.alert_text = alert.text
            print(f"Alert present: {self.alert_text}")
            # Accept the alert to dismiss it and continue with the test
            alert.accept()
        except NoAlertPresentException:
            # No alert present, continue with the test
            pass
        
        return self
        
    def click_register_link(self):
        """Click the register link"""
        self.driver.find_element(*self.REGISTER_LINK).click()
        return self
    
    def login(self, email: str, password: str):
        """Complete the entire login process"""
        self.set_email(email)
        self.set_password(password)
        self.click_login()
        return self
    
    def get_email_error(self):
        """Get the email field error message if present"""
        try:
            return self.driver.find_element(*self.EMAIL_ERROR).text
        except:
            return None
            
    def get_password_error(self):
        """Get the password field error message if present"""
        try:
            return self.driver.find_element(*self.PASSWORD_ERROR).text
        except:
            return None
            
    def get_server_error(self):
        """Get the server error message if present"""
        try:
            return self.driver.find_element(*self.SERVER_ERROR).text
        except:
            return None
    
    def is_at_login_page(self):
        """Check if we're at the login page"""
        return "/login" in self.driver.current_url
    
    def wait_for_redirection(self, timeout=10):
        """Wait for redirection after successful login"""
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda driver: "/login" not in driver.current_url
            )
            return True
        except:
            return False
    
    def get_alert_text(self):
        """Get the stored alert text if any"""
        return self.alert_text 