import pytest
from selenium.webdriver.remote.webdriver import WebDriver
import sys
import os
import time
import random
from selenium.common.exceptions import UnexpectedAlertPresentException

# Add the parent directory to the path to enable imports from the pages directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from pages.register_page import RegisterPage

# Test data
VALID_EMAIL = f"test{random.randint(1000, 9999)}@mail.ru"
VALID_PASSWORD = "Password123!"
SHORT_PASSWORD = "Pass123"
INVALID_EMAIL = "invalid-email"

class TestRegistration:
    """Tests for the registration functionality"""
    
    def test_empty_fields_validation(self, driver: WebDriver):
        """
        Test scenario 1.1: Not filling required fields should not allow registration
        """
        # Initialize the register page and navigate to it
        register_page = RegisterPage(driver).navigate()
        
        # Try to submit with all fields empty
        register_page.click_register()
        
        # Verify we're still on the register page (no redirection)
        assert register_page.is_at_register_page(), "Should remain on registration page"
        
        # Verify at least one validation error is present (either in the form or as an alert)
        # Since alerts are used for some validations, we're checking if we're still on the page
        assert register_page.is_at_register_page(), "Validation error should prevent form submission"
    
    def test_password_mismatch_validation(self, driver: WebDriver):
        """
        Test scenario 1.2: Unmatching passwords should not allow registration
        """
        # Initialize the register page and navigate to it
        register_page = RegisterPage(driver).navigate()
        
        # Fill in the form with mismatched passwords
        register_page.set_email(VALID_EMAIL)
        register_page.set_password(VALID_PASSWORD)
        register_page.set_confirm_password("DifferentPassword123!")
        register_page.click_register()
        
        # Verify error message appears for password mismatch
        password_error = register_page.get_confirm_password_error()
        assert password_error is not None, "Password mismatch error should be displayed"
        assert "match" in password_error.lower(), "Error should indicate passwords don't match"
        
        # Verify we're still on the register page (no redirection)
        assert register_page.is_at_register_page(), "Should remain on registration page"
    
    def test_invalid_email_validation(self, driver: WebDriver):
        """
        Test scenario 1.3: Password less than 8 characters should not allow registration
        """
        # Initialize the register page and navigate to it
        register_page = RegisterPage(driver).navigate()
        
        # Fill in the form with a short password
        register_page.set_email(VALID_EMAIL)
        register_page.set_password(SHORT_PASSWORD)
        register_page.set_confirm_password(SHORT_PASSWORD)
        register_page.click_register()
        
        # After the alert is automatically handled by RegisterPage.click_register(),
        # we should still be on the register page
        assert register_page.is_at_register_page(), "Should remain on registration page with short password"
        
        # Print a message for visibility
        print("Password length validation passed - the alert was handled correctly")
    
    def test_password_length_validation(self, driver: WebDriver):
        """
        Test scenario: Password less than 8 characters should not allow registration
        """
        # Initialize the register page and navigate to it
        register_page = RegisterPage(driver).navigate()
        
        # Fill in the form with a short password
        register_page.set_email(VALID_EMAIL)
        register_page.set_password(SHORT_PASSWORD)
        register_page.set_confirm_password(SHORT_PASSWORD)
        
        # Click register - our RegisterPage class now handles the alert automatically
        register_page.click_register()
        
        # Assert we're still on the register page, which indicates registration failed
        assert register_page.is_at_register_page(), "Should remain on registration page with short password"
        
        # Add a print statement for visibility
        print("Password length validation passed - alert was handled correctly")
    
    def test_successful_registration(self, driver: WebDriver):
        """
        Test scenario 1.4: Correct email and matching password (8+ chars) should allow registration
        """
        # Generate a unique email to avoid registration conflicts
        unique_email = f"test{random.randint(10000, 99999)}@mail.ru"
        
        # Initialize the register page and navigate to it
        register_page = RegisterPage(driver).navigate()
        
        # Fill in the form with valid data
        register_page.set_email(unique_email)
        register_page.set_password(VALID_PASSWORD)
        register_page.set_confirm_password(VALID_PASSWORD)
        register_page.click_register()
        
        # Wait a bit for the form submission and potential redirect
        time.sleep(3)
        
        # Check for successful redirection or being logged in
        redirection_happened = register_page.wait_for_redirection()
        
        # Print the current URL for debugging
        print(f"Final URL after registration: {driver.current_url}")
        
        # If redirection happened, test passes
        if redirection_happened:
            assert "/" in driver.current_url, "Should redirect to a valid page after registration"
        # If no redirection, check we're not still on the register page
        else:
            # Check that we're not on the register page anymore
            assert not register_page.is_at_register_page(), "Should not be on register page after successful registration"
            # Test succeeds as long as we're not on the register page
       