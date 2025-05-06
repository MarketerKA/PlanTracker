from selenium.webdriver.common.by import By
from .base_page import BasePage

class LoginPage(BasePage):
    """Page Object для страницы логина"""
    
    # Локаторы элементов, обновленные в соответствии с реальной структурой страницы
    EMAIL_INPUT = (By.CSS_SELECTOR, "input[type='email']")
    PASSWORD_INPUT = (By.CSS_SELECTOR, "input[type='password']")
    LOGIN_BUTTON = (By.CSS_SELECTOR, "button._button_xmbw2_1._primary_xmbw2_19._submitButton_ou5mw_22")
    REGISTER_LINK = (By.CSS_SELECTOR, "button._registerLink_ou5mw_44")
    FORGOT_PASSWORD_LINK = (By.XPATH, "//a[contains(text(), 'Forgot password?')]")
    ERROR_MESSAGE = (By.CLASS_NAME, "error-message")  # предполагаемый класс
    
    def __init__(self, driver, base_url):
        super().__init__(driver, base_url)
    
    def open_login_page(self):
        """Открыть страницу логина"""
        # Открывать путь login относительно базового URL
        return self.open("login")
    
    def enter_email(self, email):
        """Ввести email"""
        self.type_text(self.EMAIL_INPUT, email)
        return self
    
    def enter_password(self, password):
        """Ввести пароль"""
        self.type_text(self.PASSWORD_INPUT, password)
        return self
    
    def click_login_button(self):
        """Нажать кнопку входа"""
        self.click(self.LOGIN_BUTTON)
        return self
    
    def click_register_link(self):
        """Нажать на кнопку регистрации"""
        self.click(self.REGISTER_LINK)
        return self
    
    def click_forgot_password_link(self):
        """Нажать на ссылку восстановления пароля"""
        self.click(self.FORGOT_PASSWORD_LINK)
        return self
    
    def get_error_message(self):
        """Получить текст сообщения об ошибке"""
        if self.is_element_present(self.ERROR_MESSAGE):
            return self.get_text(self.ERROR_MESSAGE)
        return None
    
    def login(self, email, password):
        """
        Выполнить полный процесс логина
        Возвращает True, если перенаправлен на страницу после успешного логина
        """
        self.enter_email(email)
        self.enter_password(password)
        self.click_login_button()
        
        # Проверяем, что мы перенаправлены на главную страницу после успешного логина
        # Предполагается, что URL содержит "/tasks" после успешного логина
        return self.wait_for_url_to_contain("/tasks") 