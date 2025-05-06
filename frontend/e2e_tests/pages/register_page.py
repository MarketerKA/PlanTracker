from selenium.webdriver.common.by import By
from .base_page import BasePage

class RegisterPage(BasePage):
    """Page Object для страницы регистрации"""
    
    # Упрощенные локаторы элементов
    EMAIL_INPUT = (By.CSS_SELECTOR, "input[type='email']")
    PASSWORD_INPUT = (By.XPATH, "(//input[@type='password'])[1]")
    CONFIRM_PASSWORD_INPUT = (By.XPATH, "(//input[@type='password'])[2]")
    REGISTER_BUTTON = (By.XPATH, "//button[contains(text(), 'Register')]")
    LOGIN_LINK = (By.XPATH, "//button[contains(text(), 'Log in')]")
    ERROR_MESSAGE = (By.CLASS_NAME, "_serverError_1v302_7")
    
    def __init__(self, driver, base_url):
        super().__init__(driver, base_url)
    
    def open_register_page(self):
        """Открыть страницу регистрации"""
        return self.open("register")
    
    def enter_email(self, email):
        """Ввести email"""
        self.type_text(self.EMAIL_INPUT, email)
        return self
    
    def enter_password(self, password):
        """Ввести пароль"""
        self.type_text(self.PASSWORD_INPUT, password)
        return self
    
    def enter_confirm_password(self, password):
        """Ввести подтверждение пароля"""
        self.type_text(self.CONFIRM_PASSWORD_INPUT, password)
        return self
    
    def click_register_button(self):
        """Нажать кнопку регистрации"""
        self.click(self.REGISTER_BUTTON)
        return self
    
    def click_login_link(self):
        """Нажать на ссылку входа"""
        self.click(self.LOGIN_LINK)
        return self
    
    def get_error_message(self):
        """Получить текст сообщения об ошибке"""
        if self.is_element_present(self.ERROR_MESSAGE):
            return self.get_text(self.ERROR_MESSAGE)
        return None
    
    def register(self, email, password, confirm_password=None):
        """
        Выполнить полный процесс регистрации
        
        Args:
            email: Email пользователя
            password: Пароль пользователя
            confirm_password: Подтверждение пароля (если None, используется password)
            
        Returns:
            bool: True, если перенаправлен на домашнюю страницу
        """
        if confirm_password is None:
            confirm_password = password
            
        self.enter_email(email)
        self.enter_password(password)
        self.enter_confirm_password(confirm_password)
        self.click_register_button()
        
        # Ждем перенаправления на домашнюю страницу (если успешно)
        try:
            return self.wait_for_url_to_contain("home")
        except:
            return False 