#!/usr/bin/env python
import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from pages.register_page import RegisterPage

def check_register_structure(url):
    """Проверить структуру страницы регистрации и сделать скриншот"""
    print(f"Открываем страницу регистрации: {url}")
    
    # Настройка драйвера
    options = webdriver.ChromeOptions()
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    
    try:
        # Открыть страницу
        driver.get(url)
        print("Страница регистрации загружена")
        
        # Ждем, чтобы страница полностью загрузилась
        time.sleep(3)
        
        # Сделать скриншот
        screenshot_path = os.path.join(os.getcwd(), "register_screenshot.png")
        driver.save_screenshot(screenshot_path)
        print(f"Скриншот сохранен: {screenshot_path}")
        
        # Получить структуру страницы
        page_source = driver.page_source
        
        # Получить все input элементы
        inputs = driver.find_elements("tag name", "input")
        print("\nНайдены input элементы:")
        for i, input_elem in enumerate(inputs):
            input_type = input_elem.get_attribute("type")
            input_id = input_elem.get_attribute("id") or "нет id"
            input_name = input_elem.get_attribute("name") or "нет name"
            input_class = input_elem.get_attribute("class") or "нет class"
            print(f"{i+1}. Type: {input_type}, ID: {input_id}, Name: {input_name}, Class: {input_class}")
        
        # Получить все button элементы
        buttons = driver.find_elements("tag name", "button")
        print("\nНайдены button элементы:")
        for i, button in enumerate(buttons):
            button_text = button.text or "нет текста"
            button_id = button.get_attribute("id") or "нет id"
            button_class = button.get_attribute("class") or "нет class"
            print(f"{i+1}. Text: {button_text}, ID: {button_id}, Class: {button_class}")
        
        # Сохранить HTML-структуру в файл
        html_path = os.path.join(os.getcwd(), "register_structure.html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(page_source)
        print(f"HTML-структура сохранена: {html_path}")
        
    finally:
        # Закрыть браузер
        driver.quit()

def try_register_user(url, email, password):
    """Попытка регистрации пользователя"""
    print(f"Открываем страницу регистрации для регистрации: {url}")
    
    # Настройка драйвера
    options = webdriver.ChromeOptions()
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    base_url = url.split("/register")[0]
    
    try:
        # Создаем объект RegisterPage
        register_page = RegisterPage(driver, base_url)
        register_page.open_register_page()
        print("Страница регистрации загружена")
        
        # Скриншот до регистрации
        driver.save_screenshot("before_register.png")
        
        # Выполняем регистрацию
        print(f"Пытаемся зарегистрировать пользователя: {email}")
        success = register_page.register(email, password, password)
        
        # Ждем завершения процесса
        time.sleep(5)
        
        # Скриншот после регистрации
        driver.save_screenshot("after_register.png")
        
        # Выводим результат
        current_url = driver.current_url
        print(f"URL после регистрации: {current_url}")
        print(f"Регистрация {'успешна' if success else 'не удалась'}")
        
        # Проверяем, есть ли сообщение об ошибке
        error_message = register_page.get_error_message()
        if error_message:
            print(f"Сообщение об ошибке: {error_message}")
        
        # Сохраняем HTML-структуру
        html_path = os.path.join(os.getcwd(), "after_register.html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        
        return success
        
    finally:
        # Закрыть браузер
        driver.quit()

if __name__ == "__main__":
    # URL страницы регистрации
    url = "http://localhost:5173/PlanTracker/register"
    
    # Сначала проверим структуру страницы
    check_register_structure(url)
    
    # Затем попробуем зарегистрировать пользователя
    email = "test_user@example.com"
    password = "password123"
    try_register_user(url, email, password) 