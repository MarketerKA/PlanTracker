#!/usr/bin/env python
import os
import argparse
from utils.deploy_utils import GitHubPagesDeployer

def main():
    """
    Основная функция для запуска деплоя на GitHub Pages
    """
    parser = argparse.ArgumentParser(description='Deploy frontend to GitHub Pages')
    
    parser.add_argument('--username', type=str, help='GitHub username', 
                        default=os.environ.get('GITHUB_USERNAME'))
    parser.add_argument('--token', type=str, help='GitHub personal access token', 
                        default=os.environ.get('GITHUB_TOKEN'))
    parser.add_argument('--repository', type=str, help='GitHub repository (format: username/repo)', 
                        default=os.environ.get('GITHUB_REPOSITORY', 'MarketerKA/PlanTracker'))
    parser.add_argument('--headless', action='store_true', help='Run browser in headless mode')
    parser.add_argument('--wait', action='store_true', help='Wait for deployment to complete', default=True)
    parser.add_argument('--timeout', type=int, help='Maximum wait time in minutes', default=10)
    
    args = parser.parse_args()
    
    # Проверка обязательных аргументов
    if not args.username:
        print("Ошибка: не указано имя пользователя GitHub")
        print("Укажите имя пользователя через аргумент --username или переменную окружения GITHUB_USERNAME")
        return 1
    
    if not args.token:
        print("Ошибка: не указан токен GitHub")
        print("Укажите токен через аргумент --token или переменную окружения GITHUB_TOKEN")
        return 1
    
    print(f"Запуск деплоя на GitHub Pages для {args.repository}...")
    
    # Создание и запуск деплойера
    deployer = GitHubPagesDeployer(args.username, args.token, args.repository)
    success = deployer.deploy(
        headless=args.headless, 
        wait_for_completion=args.wait
    )
    
    if success:
        print("Деплой успешно завершен или запущен")
        print(f"Сайт будет доступен по адресу: https://{args.username.lower()}.github.io/{args.repository.split('/')[1]}/")
        return 0
    else:
        print("Деплой завершился с ошибкой. Проверьте логи для получения дополнительной информации.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code) 