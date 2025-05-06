#!/usr/bin/env python
import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

def check_login_redirect(url, email, password):
    """Проверить перенаправление после входа в систему"""
    print(f"Открываем страницу: {url}")
    
    # Настройка драйвера
    options = webdriver.ChromeOptions()
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    
    try:
        # Открыть страницу
        driver.get(url)
        print("Страница логина загружена")
        
        # Ждем, чтобы страница полностью загрузилась
        time.sleep(3)
        
        # Находим поля ввода и кнопку
        email_input = driver.find_element(By.CSS_SELECTOR, "input[type='email']")
        password_input = driver.find_element(By.CSS_SELECTOR, "input[type='password']")
        login_button = driver.find_element(By.CSS_SELECTOR, "button._button_xmbw2_1._primary_xmbw2_19._submitButton_ou5mw_22")
        
        # Вводим учетные данные
        email_input.clear()
        email_input.send_keys(email)
        password_input.clear()
        password_input.send_keys(password)
        
        # Делаем скриншот перед входом
        driver.save_screenshot("before_login.png")
        print("Скриншот перед входом сохранен: before_login.png")
        
        # Нажимаем кнопку входа
        login_button.click()
        print("Нажали кнопку входа")
        
        # Ждем перенаправления
        time.sleep(5)
        
        # Делаем скриншот после входа
        driver.save_screenshot("after_login.png")
        print("Скриншот после входа сохранен: after_login.png")
        
        # Выводим URL после входа
        current_url = driver.current_url
        print(f"URL после входа: {current_url}")
        
        # Проверяем, есть ли сообщение об ошибке
        try:
            error_elements = driver.find_elements(By.CSS_SELECTOR, "._errorMessage_ou5mw_26")
            if error_elements:
                print(f"Найдено сообщение об ошибке: {error_elements[0].text}")
            else:
                print("Сообщений об ошибке не найдено")
        except Exception as e:
            print(f"Ошибка при поиске сообщения об ошибке: {e}")
        
        # Проверяем, какие элементы есть на странице после входа
        elements = driver.find_elements(By.CSS_SELECTOR, "*")
        print(f"Всего элементов на странице: {len(elements)}")
        
        # Сохраняем HTML-структуру
        html_path = os.path.join(os.getcwd(), "after_login.html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print(f"HTML-структура после входа сохранена: {html_path}")
        
    finally:
        # Закрыть браузер
        driver.quit()

if __name__ == "__main__":
    # URL страницы логина и учетные данные
    url = "http://localhost:5173/PlanTracker/login"
    email = "test@example.com"
    password = "password123"
    check_login_redirect(url, email, password) 