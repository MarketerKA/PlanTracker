#!/usr/bin/env python
import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

def check_page_structure(url):
    """Проверить структуру страницы и сделать скриншот"""
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
        print("Страница загружена")
        
        # Ждем, чтобы страница полностью загрузилась
        time.sleep(3)
        
        # Сделать скриншот
        screenshot_path = os.path.join(os.getcwd(), "page_screenshot.png")
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
        
        # Получить все ссылки
        links = driver.find_elements("tag name", "a")
        print("\nНайдены ссылки:")
        for i, link in enumerate(links):
            link_text = link.text or "нет текста"
            link_href = link.get_attribute("href") or "нет href"
            print(f"{i+1}. Text: {link_text}, Href: {link_href}")
        
        # Сохранить HTML-структуру в файл
        html_path = os.path.join(os.getcwd(), "page_structure.html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(page_source)
        print(f"HTML-структура сохранена: {html_path}")
        
    finally:
        # Закрыть браузер
        driver.quit()

if __name__ == "__main__":
    # URL страницы логина
    url = "http://localhost:5173/PlanTracker/login"
    check_page_structure(url) 