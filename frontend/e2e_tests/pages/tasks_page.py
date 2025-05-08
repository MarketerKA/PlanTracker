from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys
import os
import time

# Add the parent directory to the path to enable imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from conftest import BASE_URL

class TasksPage:
    # URL
    URL = f"{BASE_URL}/tasks"
    
    # Header Locators
    LOGOUT_BUTTON = (By.CSS_SELECTOR, "button._button_xmbw2_1._secondary_xmbw2_24")
    USER_EMAIL = (By.CSS_SELECTOR, ".userEmail")
    LOGIN_BUTTON = (By.CSS_SELECTOR, "button._button_xmbw2_1._primary_xmbw2_19._submitButton_ou5mw_22")
    
    # Tasks Tab Locators
    TASKS_TAB = (By.XPATH, "//button[contains(text(), 'Tasks')]")
    STATISTICS_TAB = (By.XPATH, "//button[contains(text(), 'Statistics')]")
    
    def __init__(self, driver: WebDriver):
        self.driver = driver
        
    def navigate(self):
        """Navigate to the tasks page"""
        self.driver.get(self.URL)
        return self
    
    def navigate_to_home(self):
        """Navigate to the home page where header is also present"""
        self.driver.get(BASE_URL)
        return self
        
    # Header related methods
    def click_logout(self):
        """Click the logout button in the header"""
        try:
            logout_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(self.LOGOUT_BUTTON)
            )
            logout_button.click()
            time.sleep(1)  # Allow time for logout action to complete
        except:
            print("Logout button not found or not clickable")
        return self
    
    def is_logged_in(self):
        """Check if the user is logged in by looking for the user email display"""
        try:
            WebDriverWait(self.driver, 5).until(
                EC.visibility_of_element_located(self.USER_EMAIL)
            )
            return True
        except:
            return False
    
    def wait_for_logout_completed(self, timeout=10):
        """Wait for the logout process to complete (login button appears)"""
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.invisibility_of_element_located(self.USER_EMAIL)
            )
            # Verify login button appears
            WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(self.LOGIN_BUTTON)
            )
            return True
        except:
            return False
    
    def get_user_email(self):
        """Get the displayed user email if logged in"""
        try:
            return self.driver.find_element(*self.USER_EMAIL).text
        except:
            return None
            
    # Tasks related methods
    def switch_to_tasks_tab(self):
        """Switch to the Tasks tab"""
        try:
            self.driver.find_element(*self.TASKS_TAB).click()
            time.sleep(0.5)  # Wait for tab switch
        except:
            print("Tasks tab not found or not clickable")
        return self
        
    def switch_to_statistics_tab(self):
        """Switch to the Statistics tab"""
        try:
            self.driver.find_element(*self.STATISTICS_TAB).click()
            time.sleep(0.5)  # Wait for tab switch
        except:
            print("Statistics tab not found or not clickable")
        return self 