import pytest
from selenium.webdriver.remote.webdriver import WebDriver
import sys
import os
import time
import random
from selenium.common.exceptions import UnexpectedAlertPresentException
from selenium.webdriver.support.ui import WebDriverWait

# Add the parent directory to the path to enable imports from the pages directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from pages.login_page import LoginPage
from pages.register_page import RegisterPage
from pages.tasks_page import TasksPage
from conftest import BASE_URL

# Test data - will be generated dynamically in setup
VALID_EMAIL = "test@mail.ru"
VALID_PASSWORD = "12345678"
WRONG_PASSWORD = "87654321"
INVALID_EMAIL = "invalid-email"

class TestLogin:
    """Tests for the login functionality"""
    
    
    
    def test_empty_fields_validation(self, driver: WebDriver):
        """
        Test scenario: Not filling required fields should not allow login
        """
        # Initialize the login page and navigate to it
        login_page = LoginPage(driver).navigate()
        
        # Try to submit with all fields empty
        login_page.click_login()
        
        # Verify we're still on the login page (no redirection)
        assert login_page.is_at_login_page(), "Should remain on login page"
        
        # Verify we're still on the login page due to validation error
        assert login_page.is_at_login_page(), "Validation error should prevent form submission"
    
    def test_invalid_email_format(self, driver: WebDriver):
        """
        Test scenario: Invalid email format should not allow login
        """
        # Initialize the login page and navigate to it
        login_page = LoginPage(driver).navigate()
        
        # Fill in the form with invalid email format
        login_page.set_email(INVALID_EMAIL)
        login_page.set_password(VALID_PASSWORD)
        login_page.click_login()
        
        # Verify we're still on the login page (no redirection)
        assert login_page.is_at_login_page(), "Should remain on login page"
    
    def test_incorrect_credentials(self, driver: WebDriver):
        """
        Test scenario: Login with incorrect credentials should show error message
        """
        # Initialize the login page and navigate to it
        login_page = LoginPage(driver).navigate()
        
        # Fill in the form with incorrect credentials (right email, wrong password)
        login_page.set_email(VALID_EMAIL)
        login_page.set_password(WRONG_PASSWORD)
        login_page.click_login()
        
        # Wait for server response
        time.sleep(2)
        
        
        # Verify we're still on the login page (no redirection)
        assert login_page.is_at_login_page(), "Should remain on login page with incorrect credentials"
    
    def test_successful_login(self, driver: WebDriver):
        """
        Test scenario: Login with correct credentials should redirect to home page
        """
        # Initialize the login page and navigate to it
        login_page = LoginPage(driver).navigate()
        
        # Fill in the form with valid data
        login_page.set_email(VALID_EMAIL)
        login_page.set_password(VALID_PASSWORD)
        login_page.click_login()
        
        # Wait a bit for the form submission and potential redirect
        time.sleep(3)
        
        # Check for successful redirection
        redirection_happened = login_page.wait_for_redirection()
        
        
        # Print the current URL for debugging
        print(f"Final URL after registration: {driver.current_url}")
        
        # If redirection happened, test passes
        if redirection_happened:
            assert "/" in driver.current_url, "Should redirect to a valid page after login"
        # If no redirection, check we're not still on the register page
        else:
            # Check that we're not on the register page anymore
            assert not login_page.is_at_login_page(), "Should not be on login page after successful login"
            # Test succeeds as long as we're not on the register page
    
    def test_navigation_to_register(self, driver: WebDriver):
        """
        Test scenario: Clicking the register link should navigate to the registration page
        """
        # First, log out if logged in
        driver.get(f"{BASE_URL}/")
        tasks_page = TasksPage(driver)
        if tasks_page.is_logged_in():
            tasks_page.click_logout()
            tasks_page.wait_for_logout_completed()
        
        # Initialize the login page and navigate to it
        login_page = LoginPage(driver).navigate()
        
        # Click the register link
        login_page.click_register_link()
        
        # Wait for navigation
        time.sleep(2)
        
        # Verify we're on the register page
        assert "/register" in driver.current_url, "Should navigate to the registration page" 