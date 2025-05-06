from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import logging

# Настройка логгера
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BasePage:
    """Базовый класс для всех страниц приложения"""
    
    def __init__(self, driver, base_url):
        self.driver = driver
        self.base_url = base_url
        self.wait = WebDriverWait(driver, 10)
        self.logger = logger
    
    def open(self, url_path=""):
        """Открыть страницу по относительному пути"""
        full_url = f"{self.base_url}/{url_path}"
        self.logger.info(f"Opening URL: {full_url}")
        self.driver.get(full_url)
        return self
    
    def find_element(self, locator, timeout=10):
        """Найти элемент с ожиданием его появления"""
        try:
            self.logger.debug(f"Finding element: {locator}")
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(locator)
            )
            return element
        except TimeoutException:
            self.logger.error(f"Element not found within {timeout} seconds: {locator}")
            raise
    
    def click(self, locator):
        """Нажать на элемент"""
        element = self.find_element(locator)
        self.logger.debug(f"Clicking on element: {locator}")
        element.click()
        return self
    
    def type_text(self, locator, text):
        """Ввести текст в поле ввода"""
        element = self.find_element(locator)
        self.logger.debug(f"Typing '{text}' into element: {locator}")
        element.clear()
        element.send_keys(text)
        return self
    
    def is_element_present(self, locator, timeout=5):
        """Проверить наличие элемента на странице"""
        try:
            self.find_element(locator, timeout)
            return True
        except (TimeoutException, NoSuchElementException):
            return False
    
    def get_text(self, locator):
        """Получить текст элемента"""
        element = self.find_element(locator)
        text = element.text
        self.logger.debug(f"Got text from element {locator}: {text}")
        return text
    
    def wait_for_url_to_contain(self, text, timeout=10):
        """Ожидание, пока URL не будет содержать указанный текст"""
        try:
            WebDriverWait(self.driver, timeout).until(EC.url_contains(text))
            return True
        except TimeoutException:
            current_url = self.driver.current_url
            self.logger.error(f"URL does not contain '{text}' within {timeout} seconds. Current URL: {current_url}")
            return False 