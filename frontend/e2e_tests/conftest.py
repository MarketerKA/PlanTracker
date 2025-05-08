import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import os
import time

# Base URL for the application
BASE_URL = os.environ.get("APP_URL", "http://localhost:5173")

@pytest.fixture(scope="function")
def driver():
    """
    Setup and teardown for the WebDriver.
    This fixture provides a configured Chrome WebDriver for each test function.
    """
    # Setup Chrome options
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # Run in headless mode (no GUI)
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")  # Set window size
    
    try:
        # Try creating the driver without specifying a service
        driver = webdriver.Chrome(options=chrome_options)
    except:
        # If that fails, try with default ChromeDriver
        print("Warning: Using default Chrome driver initialization. If this fails, please download "
              "the appropriate ChromeDriver for your Chrome version and specify its path.")
        driver = webdriver.Chrome(options=chrome_options)
    
    driver.implicitly_wait(10)  # Wait up to 10 seconds for elements to appear
    
    # Return the WebDriver instance to the test
    yield driver
    
    # Teardown - close the browser
    driver.quit() 