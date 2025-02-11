import os
import django
import json

# Настройка Django (замени 'your_project' на имя вашего проекта)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'work.settings')  # Замените 'work' на имя вашего проекта
django.setup()

# Импорт моделей после настройки Django
from jobs.models import Category, SubCategory  # Замените 'jobs' на имя вашего приложения


# Функция для импорта категорий и подкатегорий из JSON файла
def import_categories_from_json(file_path):
    # Открываем и читаем файл
    with open(file_path, 'r', encoding='utf-8') as file:
        categories_data = json.load(file)

    # Перебираем данные из файла и создаем категории и подкатегории
    for category_data in categories_data["specializations"]:
        category_name = category_data["category"]
        icon_name = category_data.get("icon", "")  # Получаем иконку, если есть

        # Создаем категорию с иконкой
        category, created = Category.objects.get_or_create(
            name=category_name,
            defaults={"icon": icon_name}
        )

        # Если категория уже существовала, обновляем иконку, если она не задана
        if not created and not category.icon:
            category.icon = icon_name
            category.save()

        # Создаем подкатегории для этой категории
        for subcategory_name in category_data["subcategories"]:
            SubCategory.objects.get_or_create(category=category, name=subcategory_name)

        print(f'Категория "{category.name}" и её подкатегории были успешно добавлены.')


# Вызов функции для импорта данных
if __name__ == '__main__':
    import_categories_from_json('categories.json')  # Укажите путь к вашему JSON файлу