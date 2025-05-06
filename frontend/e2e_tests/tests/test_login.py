import pytest
from pages.login_page import LoginPage

class TestLogin:
    """Тесты для функционала входа в систему"""
    
    @pytest.mark.parametrize(
        "email,password,expected_success", 
        [
            ("test@example.com", "password123", True),  # валидные данные
            ("invalid@example.com", "wrongpassword", False),  # неверные данные
            ("", "password123", False),  # пустой email
            ("test@example.com", "", False),  # пустой пароль
        ]
    )
    def test_login_scenarios(self, driver, base_url, email, password, expected_success):
        """Проверка различных сценариев входа в систему"""
        login_page = LoginPage(driver, base_url)
        login_page.open_login_page()
        
        # Выполнить попытку входа
        success = login_page.login(email, password)
        
        # Проверка результата
        assert success == expected_success, f"Login with {email}/{password} should be {'successful' if expected_success else 'unsuccessful'}"
        
        # Если вход не должен быть успешным, проверяем наличие сообщения об ошибке
        if not expected_success:
            error_message = login_page.get_error_message()
            assert error_message is not None, "Error message should be displayed for invalid login"
    
    def test_navigation_to_register(self, driver, base_url):
        """Проверка навигации на страницу регистрации"""
        login_page = LoginPage(driver, base_url)
        login_page.open_login_page()
        
        # Нажать на ссылку регистрации
        login_page.click_register_link()
        
        # Проверить, что URL содержит "register"
        assert login_page.wait_for_url_to_contain("register"), "URL should contain 'register'" 