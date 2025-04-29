#!/usr/bin/env python
"""
Скрипт для создания пользователей в AvitoRentPro.
Запуск: python -m scripts.create_user [--email EMAIL] [--password PASSWORD] [--role ROLE]
                                      [--first_name FIRST_NAME] [--last_name LAST_NAME]
"""

import sys
import os
import logging
import argparse
from getpass import getpass

# Добавляем путь к корневой директории проекта
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.db.database import SessionLocal
from src.models.auth import User, initialize_permissions
from src.services.auth import hash_password, validate_password

# Настройка логгера
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def create_user(
        email,
        password,
        role="manager",
        first_name=None,
        last_name=None,
        is_active=True,
        interactive=True
):
    """
    Создает нового пользователя.

    Args:
        email (str): Email пользователя
        password (str): Пароль пользователя
        role (str, optional): Роль пользователя ("owner" или "manager"). По умолчанию "manager".
        first_name (str, optional): Имя пользователя
        last_name (str, optional): Фамилия пользователя
        is_active (bool, optional): Статус активности пользователя. По умолчанию True.
        interactive (bool, optional): Включить интерактивный режим. По умолчанию True.

    Returns:
        bool: True если пользователь успешно создан, иначе False
    """
    db = SessionLocal()
    try:
        # Проверяем, существует ли пользователь с таким email
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            logger.error(f"Пользователь с email {email} уже существует")
            return False

        # Проверяем корректность роли
        if role not in ["owner", "manager"]:
            logger.error(f"Недопустимая роль: {role}. Допустимые роли: owner, manager")
            return False

        # Проверяем сложность пароля
        is_valid, password_error = validate_password(password)
        if not is_valid:
            logger.error(f"Некорректный пароль: {password_error}")
            return False

        # Инициализируем разрешения для ролей
        initialize_permissions(db)

        # Создаем пользователя
        new_user = User(
            email=email,
            password_hash=hash_password(password),
            first_name=first_name,
            last_name=last_name,
            role=role,
            is_active=is_active
        )

        db.add(new_user)
        db.commit()

        if interactive:
            logger.info(f"Пользователь успешно создан: {email} (роль: {role})")
        return True

    except Exception as e:
        db.rollback()
        logger.error(f"Ошибка при создании пользователя: {e}")
        return False

    finally:
        db.close()


def interactive_mode():
    """Запускает интерактивный режим создания пользователя."""
    print("=== Создание нового пользователя ===")

    email = input("Email пользователя: ")

    while True:
        password = getpass("Пароль: ")
        password_confirm = getpass("Подтверждение пароля: ")

        if password != password_confirm:
            print("Пароли не совпадают. Попробуйте снова.")
            continue

        is_valid, password_error = validate_password(password)
        if not is_valid:
            print(f"Некорректный пароль: {password_error}")
            continue

        break

    print("\nДоступные роли:")
    print("1. owner - владелец (все права)")
    print("2. manager - менеджер (ограниченные права)")

    while True:
        role_choice = input("Выберите роль (1 или 2): ")
        if role_choice == "1":
            role = "owner"
            break
        elif role_choice == "2":
            role = "manager"
            break
        else:
            print("Неверный выбор. Пожалуйста, выберите 1 или 2.")

    first_name = input("Имя (необязательно): ").strip() or None
    last_name = input("Фамилия (необязательно): ").strip() or None

    is_active_input = input("Активировать пользователя? (y/n, по умолчанию y): ").lower()
    is_active = is_active_input != "n"

    print("\nСоздание пользователя...")
    result = create_user(
        email=email,
        password=password,
        role=role,
        first_name=first_name,
        last_name=last_name,
        is_active=is_active
    )

    if result:
        print("\n✅ Пользователь успешно создан!")
    else:
        print("\n❌ Не удалось создать пользователя.")


def main():
    parser = argparse.ArgumentParser(description="Создание пользователя для AvitoRentPro")
    parser.add_argument("--email", help="Email пользователя")
    parser.add_argument("--password", help="Пароль пользователя")
    parser.add_argument("--role", choices=["owner", "manager"], default="manager", help="Роль пользователя")
    parser.add_argument("--first_name", help="Имя пользователя")
    parser.add_argument("--last_name", help="Фамилия пользователя")
    parser.add_argument("--inactive", action="store_true", help="Создать неактивного пользователя")

    args = parser.parse_args()

    # Если переданы аргументы, создаем пользователя без интерактивного режима
    if args.email and args.password:
        is_active = not args.inactive
        result = create_user(
            email=args.email,
            password=args.password,
            role=args.role,
            first_name=args.first_name,
            last_name=args.last_name,
            is_active=is_active,
            interactive=True
        )
        if result:
            print(f"✅ Пользователь {args.email} успешно создан!")
        else:
            print(f"❌ Не удалось создать пользователя {args.email}.")
    else:
        # Запускаем интерактивный режим
        interactive_mode()


if __name__ == "__main__":
    main()
