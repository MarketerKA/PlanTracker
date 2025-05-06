import os
import time
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Настройка логгера
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GitHubPagesDeployer:
    """Класс для автоматизации процесса деплоя на GitHub Pages с использованием Selenium"""
    
    def __init__(self, username, password, repository):
        """
        Инициализация деплойера
        
        Args:
            username (str): Имя пользователя GitHub
            password (str): Пароль или токен GitHub
            repository (str): Имя репозитория (формат: username/repo)
        """
        self.username = username
        self.password = password
        self.repository = repository
        self.driver = None
        self.logger = logger
    
    def start_browser(self, headless=False):
        """Запуск браузера"""
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument("--headless")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
        self.driver.implicitly_wait(10)
        return self
    
    def login_to_github(self):
        """Вход в GitHub"""
        self.logger.info("Выполняется вход в GitHub...")
        
        # Открыть страницу входа
        self.driver.get("https://github.com/login")
        
        # Ввести имя пользователя
        username_input = self.driver.find_element(By.ID, "login_field")
        username_input.clear()
        username_input.send_keys(self.username)
        
        # Ввести пароль
        password_input = self.driver.find_element(By.ID, "password")
        password_input.clear()
        password_input.send_keys(self.password)
        
        # Нажать кнопку входа
        self.driver.find_element(By.NAME, "commit").click()
        
        # Проверка успешного входа
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "body.logged-in"))
            )
            self.logger.info("Вход выполнен успешно")
            return True
        except TimeoutException:
            self.logger.error("Не удалось войти в GitHub")
            return False
    
    def navigate_to_repository_settings(self):
        """Переход к настройкам репозитория"""
        self.logger.info(f"Переход к настройкам репозитория {self.repository}")
        self.driver.get(f"https://github.com/{self.repository}/settings")
        
        # Проверка, что мы на странице настроек
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "nav.menu"))
            )
            self.logger.info("Успешно перешли на страницу настроек")
            return True
        except TimeoutException:
            self.logger.error("Не удалось перейти к настройкам репозитория")
            return False
    
    def navigate_to_pages_settings(self):
        """Переход к настройкам GitHub Pages"""
        self.logger.info("Переход к настройкам GitHub Pages")
        
        try:
            # Найти и кликнуть на пункт Pages в меню
            pages_menu_item = self.driver.find_element(By.XPATH, "//a[contains(text(), 'Pages')]")
            pages_menu_item.click()
            
            # Проверка, что мы на странице настроек Pages
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//h1[contains(text(), 'GitHub Pages')]"))
            )
            self.logger.info("Успешно перешли на страницу настроек GitHub Pages")
            return True
        except (TimeoutException, NoSuchElementException) as e:
            self.logger.error(f"Не удалось перейти к настройкам GitHub Pages: {e}")
            return False
    
    def configure_github_pages(self):
        """Настройка GitHub Pages"""
        self.logger.info("Настройка GitHub Pages для использования GitHub Actions")
        
        try:
            # Выбрать опцию GitHub Actions
            source_dropdown = self.driver.find_element(By.ID, "source")
            source_dropdown.click()
            
            # Выбрать опцию GitHub Actions
            github_actions_option = self.driver.find_element(By.XPATH, "//option[contains(text(), 'GitHub Actions')]")
            github_actions_option.click()
            
            # Нажать кнопку сохранения
            save_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Save')]")
            save_button.click()
            
            # Дождаться сообщения об успешном сохранении
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "flash-success"))
            )
            
            self.logger.info("GitHub Pages успешно настроен для использования GitHub Actions")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка при настройке GitHub Pages: {e}")
            return False
    
    def run_workflow(self):
        """Запуск workflow для деплоя"""
        self.logger.info("Запуск workflow для деплоя...")
        
        try:
            # Перейти на страницу Actions
            self.driver.get(f"https://github.com/{self.repository}/actions")
            
            # Нажать на кнопку "Run workflow"
            run_workflow_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Run workflow')]")
            run_workflow_button.click()
            
            # Выбрать деплой workflow
            deploy_workflow_button = self.driver.find_element(By.XPATH, "//span[contains(text(), 'Deploy Frontend to GitHub Pages')]")
            deploy_workflow_button.click()
            
            # Подтвердить запуск workflow
            confirm_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Run workflow')]")
            confirm_button.click()
            
            self.logger.info("Workflow успешно запущен")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка при запуске workflow: {e}")
            return False
    
    def check_deployment_status(self, max_wait_minutes=10):
        """Проверка статуса деплоя"""
        self.logger.info(f"Проверка статуса деплоя (ожидание до {max_wait_minutes} минут)...")
        
        # Перейти на страницу Actions
        self.driver.get(f"https://github.com/{self.repository}/actions")
        
        start_time = time.time()
        max_wait_seconds = max_wait_minutes * 60
        
        while time.time() - start_time < max_wait_seconds:
            try:
                # Проверка последнего workflow run
                status_element = self.driver.find_element(By.CSS_SELECTOR, ".workflow-run-completed-icon")
                status_text = status_element.get_attribute("aria-label")
                
                if "completed successfully" in status_text:
                    self.logger.info("Деплой успешно завершен")
                    return True
                elif "failed" in status_text:
                    self.logger.error("Деплой завершился ошибкой")
                    return False
                
                # Ждем и обновляем страницу
                time.sleep(30)
                self.driver.refresh()
            except NoSuchElementException:
                # Workflow еще выполняется
                self.logger.info("Workflow еще выполняется, ожидание...")
                time.sleep(30)
                self.driver.refresh()
        
        self.logger.error(f"Превышено максимальное время ожидания ({max_wait_minutes} минут)")
        return False
    
    def deploy(self, headless=False, wait_for_completion=True):
        """Выполнить полный процесс деплоя"""
        try:
            self.logger.info("Начало процесса деплоя на GitHub Pages")
            
            # Запуск браузера
            self.start_browser(headless)
            
            # Вход в GitHub
            if not self.login_to_github():
                return False
            
            # Настройка GitHub Pages
            if not self.navigate_to_repository_settings() or not self.navigate_to_pages_settings():
                return False
            
            if not self.configure_github_pages():
                return False
            
            # Запуск workflow
            if not self.run_workflow():
                return False
            
            # Проверка статуса деплоя
            if wait_for_completion:
                deployment_success = self.check_deployment_status()
                if deployment_success:
                    self.logger.info(f"Сайт успешно развернут по адресу: https://{self.username.lower()}.github.io/{self.repository.split('/')[1]}/")
                return deployment_success
            
            self.logger.info("Процесс деплоя запущен успешно")
            return True
        
        except Exception as e:
            self.logger.error(f"Ошибка в процессе деплоя: {e}")
            return False
        
        finally:
            # Закрытие браузера
            if self.driver:
                self.driver.quit()


if __name__ == "__main__":
    # Пример использования
    username = os.environ.get("GITHUB_USERNAME")
    password = os.environ.get("GITHUB_TOKEN")  # Лучше использовать токен, а не пароль
    repository = os.environ.get("GITHUB_REPOSITORY", "MarketerKA/PlanTracker")
    
    if not username or not password:
        print("Пожалуйста, установите переменные окружения GITHUB_USERNAME и GITHUB_TOKEN")
    else:
        deployer = GitHubPagesDeployer(username, password, repository)
        deployer.deploy(headless=False, wait_for_completion=True) 