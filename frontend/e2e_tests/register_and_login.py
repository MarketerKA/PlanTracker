#!/usr/bin/env python
import time
import os
import uuid
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from pages.register_page import RegisterPage
from pages.login_page import LoginPage

def register_and_login(base_url, email, password):
    """
    Выполняет процесс регистрации и последующего входа
    
    Args:
        base_url: Базовый URL сайта
        email: Email для регистрации и входа
        password: Пароль для регистрации и входа
    """
    print(f"Начинаем процесс регистрации и входа для пользователя: {email}")
    
    # Настройка драйвера
    options = webdriver.ChromeOptions()
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    
    try:
        # Шаг 1: Регистрация
        register_page = RegisterPage(driver, base_url)
        register_page.open_register_page()
        print("Страница регистрации загружена")
        
        # Скриншот страницы регистрации
        driver.save_screenshot("register_page.png")
        print("Скриншот страницы регистрации сохранен")
        
        # Выполнение регистрации
        print(f"Регистрация пользователя: {email}")
        register_success = register_page.register(email, password)
        time.sleep(3)
        
        # Скриншот после регистрации
        driver.save_screenshot("after_register.png")
        
        current_url = driver.current_url
        print(f"URL после регистрации: {current_url}")
        print(f"Регистрация {'успешна' if register_success else 'не удалась'}")
        
        if not register_success:
            error_message = register_page.get_error_message()
            if error_message:
                print(f"Ошибка регистрации: {error_message}")
            print("Регистрация не удалась, выход из скрипта")
            return
        
        # Если регистрация автоматически вошла в систему, выходим
        print("Выход из системы для проверки входа")
        driver.delete_all_cookies()
        
        # Шаг 2: Вход в систему
        login_page = LoginPage(driver, base_url)
        login_page.open_login_page()
        print("Страница входа загружена")
        
        # Скриншот страницы входа
        driver.save_screenshot("login_page.png")
        
        # Выполнение входа
        print(f"Вход пользователя: {email}")
        login_success = login_page.login(email, password)
        time.sleep(3)
        
        # Скриншот после входа
        driver.save_screenshot("after_login.png")
        
        current_url = driver.current_url
        print(f"URL после входа: {current_url}")
        print(f"Вход {'успешен' if login_success else 'не удался'}")
        
        if not login_success:
            error_message = login_page.get_error_message()
            if error_message:
                print(f"Ошибка входа: {error_message}")
            print("Вход не удался")
        else:
            print("Полный цикл регистрации и входа успешно завершен!")
    
    finally:
        # Закрыть браузер
        driver.quit()

if __name__ == "__main__":
    # Базовый URL приложения
    base_url = "http://localhost:5173/PlanTracker"
    
    # Генерируем уникальный email для каждого запуска
    unique_email = f"test{uuid.uuid4().hex[:8]}@example.com"
    password = "password123"
    
    print(f"Сгенерирован тестовый пользователь: {unique_email} / {password}")
    
    # Запуск процесса регистрации и входа
    register_and_login(base_url, unique_email, password) 