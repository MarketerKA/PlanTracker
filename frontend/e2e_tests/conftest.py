import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.microsoft import EdgeChromiumDriverManager

# Конфигурация для всех тестов
def pytest_addoption(parser):
    parser.addoption(
        "--browser", 
        action="store", 
        default="chrome", 
        help="Browser to run tests: chrome, firefox, or edge"
    )
    parser.addoption(
        "--headless", 
        action="store_true", 
        default=False, 
        help="Run browser in headless mode"
    )
    parser.addoption(
        "--base-url", 
        action="store", 
        default="http://localhost:5173/PlanTracker", 
        help="Base URL for the application"
    )

@pytest.fixture(scope="session")
def base_url(request):
    """Получение базового URL приложения"""
    return request.config.getoption("--base-url")

@pytest.fixture(scope="function")
def driver(request):
    """Инициализация и настройка WebDriver"""
    browser_name = request.config.getoption("--browser").lower()
    headless = request.config.getoption("--headless")
    
    # Настройка опций для выбранного браузера
    if browser_name == "chrome":
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument("--headless")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    
    elif browser_name == "firefox":
        options = webdriver.FirefoxOptions()
        if headless:
            options.add_argument("--headless")
        driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()), options=options)
    
    elif browser_name == "edge":
        options = webdriver.EdgeOptions()
        if headless:
            options.add_argument("--headless")
        driver = webdriver.Edge(service=EdgeService(EdgeChromiumDriverManager().install()), options=options)
    
    else:
        raise ValueError(f"Unsupported browser: {browser_name}")
    
    # Установка таймаутов
    driver.implicitly_wait(10)
    driver.set_page_load_timeout(30)
    
    # Передача драйвера в тест
    yield driver
    
    # Завершение работы драйвера после теста
    driver.quit() 