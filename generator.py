import os
import logging
from faker import Faker

# Налаштування логування для виводу інформації про виконання
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_random_text_files(count_files, folder, lines_per_file=100):
    """
    Створює текстові файли з випадковими реченнями.
    :param count_files: Кількість файлів, які потрібно створити
    :param folder: Папка для збереження файлів
    :param lines_per_file: Кількість рядків у кожному файлі
    """
    os.makedirs(folder, exist_ok=True)  # Переконуємося, що папка існує
    fake = Faker()  # Створюємо об'єкт для генерації випадкового тексту

    for i in range(count_files):
        file_path = os.path.join(folder, f"random_text_{i}.txt")  # Формуємо шлях до файлу
        
        # Генеруємо список випадкових речень для файлу
        lines = [fake.sentence(nb_words=10) + "\n" for _ in range(lines_per_file)]
        
        # Відкриваємо файл для запису та записуємо всі рядки одразу
        with open(file_path, "w", newline="") as file:
            file.writelines(lines)
        
        # Логування успішного створення файлу
        logging.info(f"Файл успішно створений: {file_path}")

def execute_generation():
    """
    Функція для ініціалізації генерації файлів із заданими параметрами.
    """
    create_random_text_files(count_files=100, folder="text_files", lines_per_file=1000)

if __name__ == "__main__":
    execute_generation()  # Запускаємо процес створення файлів
