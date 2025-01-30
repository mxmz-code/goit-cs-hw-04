import os
import logging
import threading
from time import time
import pprint
from collections import defaultdict
from tqdm import tqdm
from tabulate import tabulate
from colorama import Fore, Style, init

# Ініціалізація Colorama для коректного відображення кольорів
init()

# Налаштування логування
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def find_words_in_file(file_path, keywords, results):
    """
    Перевіряє наявність ключових слів у файлі та додає результати у загальний словник.
    :param file_path: Шлях до файлу
    :param keywords: Список ключових слів
    :param results: Загальний словник результатів
    """
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()
            for word in keywords:
                if word in content:
                    results[word].append(os.path.basename(file_path))
    except (FileNotFoundError, PermissionError, IOError) as e:
        logging.error(f"{Fore.RED}Помилка обробки файлу {file_path}: {e}{Style.RESET_ALL}")


def parallel_search(directory, keywords, num_threads=4):
    """
    Виконує пошук ключових слів у файлах використовуючи threading.
    :param directory: Папка з файлами
    :param keywords: Список ключових слів
    :param num_threads: Кількість потоків
    :return: Словник знайдених слів у файлах
    """
    files = [
        os.path.join(directory, f)
        for f in os.listdir(directory)
        if os.path.isfile(os.path.join(directory, f))
    ]

    results = defaultdict(list)
    threads = []
    chunk_size = len(files) // num_threads
    file_chunks = [files[i:i + chunk_size] for i in range(0, len(files), chunk_size)]

    for chunk in file_chunks:
        thread = threading.Thread(target=lambda: [find_words_in_file(f, keywords, results) for f in chunk])
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()
    
    return results


def main():
    """
    Головна функція для виконання пошуку слів у багатопоточному режимі.
    """
    keywords = ["test", "some", "example"]
    start_time = time()
    results = parallel_search("text_files", keywords, num_threads=4)
    end_time = time()

    # Форматування та виведення результатів у красивому вигляді
    table_data = []
    for keyword, files in results.items():
        file_examples = ", ".join(files[:3]) + ("..." if len(files) > 3 else "")
        table_data.append([keyword, len(files), file_examples])
    
    print(f"{Fore.GREEN}\nРезультати пошуку:{Style.RESET_ALL}")
    print(tabulate(table_data, headers=["Ключове слово", "Кількість знайдених файлів", "Приклади файлів"], tablefmt="grid"))
    print(f"\n{Fore.YELLOW}Час виконання:{Style.RESET_ALL} {end_time - start_time:.5f} секунд\n")


if __name__ == "__main__":
    main()
