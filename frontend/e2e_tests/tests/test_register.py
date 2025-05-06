import pytest
import uuid
from pages.register_page import RegisterPage
from pages.login_page import LoginPage

class TestRegister:
    """Тесты для функционала регистрации в системе"""
    
    def test_navigation_to_login(self, driver, base_url):
        """Проверка навигации со страницы регистрации на страницу входа"""
        register_page = RegisterPage(driver, base_url)
        register_page.open_register_page()
        
        # Нажать на ссылку входа
        register_page.click_login_link()
        
        # Проверить, что URL содержит "login"
        assert register_page.wait_for_url_to_contain("login"), "URL should contain 'login'"
    
    @pytest.mark.parametrize(
        "email,password,confirm_password,expected_success", 
        [
            (f"test{uuid.uuid4()}@example.com", "password123", "password123", True),  # валидные данные
            ("invalid-email", "password123", "password123", False),  # невалидный email
            (f"test{uuid.uuid4()}@example.com", "123", "123", False),  # короткий пароль
            (f"test{uuid.uuid4()}@example.com", "password123", "different123", False),  # пароли не совпадают
        ]
    )
    def test_register_scenarios(self, driver, base_url, email, password, confirm_password, expected_success):
        """Проверка различных сценариев регистрации"""
        register_page = RegisterPage(driver, base_url)
        register_page.open_register_page()
        
        # Выполнить попытку регистрации
        success = register_page.register(email, password, confirm_password)
        
        # Проверка результата
        assert success == expected_success, f"Registration with {email}/{password} should be {'successful' if expected_success else 'unsuccessful'}"
        
        # Если регистрация не должна быть успешной, проверяем наличие сообщения об ошибке или оставание на странице регистрации
        if not expected_success:
            current_url = driver.current_url
            assert "register" in current_url.lower(), "Should remain on register page after failed registration"
    
    def test_register_then_login(self, driver, base_url):
        """Проверка полного цикла: регистрация и затем вход"""
        # Генерируем уникальный email для избежания конфликтов
        unique_email = f"test{uuid.uuid4()}@example.com"
        password = "password123"
        
        # 1. Регистрация
        register_page = RegisterPage(driver, base_url)
        register_page.open_register_page()
        
        # Выполнить регистрацию
        success = register_page.register(unique_email, password)
        assert success, f"Registration with {unique_email} should be successful"
        
        # 2. Выход из системы (обычно происходит автоматически после регистрации)
        # driver.delete_all_cookies()  # Это может быть нужно в зависимости от реализации аутентификации
        
        # 3. Вход с зарегистрированными данными
        login_page = LoginPage(driver, base_url)
        login_page.open_login_page()
        
        # Выполнить вход
        login_success = login_page.login(unique_email, password)
        assert login_success, f"Login with newly registered user {unique_email} should be successful" 