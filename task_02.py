import os
import logging
import random
from multiprocessing import Process, Queue
from time import time
from collections import defaultdict
from tqdm import tqdm
from tabulate import tabulate
from colorama import Fore, Style, init
from faker import Faker

# Ініціалізація Colorama та Faker
init()
fake = Faker()


def clear_console():
    """
    Очищає екран перед запуском програми.
    """
    os.system("cls" if os.name == "nt" else "clear")


# Налаштування логування
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def generate_keywords(num_words=3):
    """
    Генерує випадкові ключові слова для пошуку.
    :param num_words: Кількість ключових слів
    :return: Список ключових слів
    """
    return [fake.word() for _ in range(num_words)]


def search_keywords_in_files(file_list, keywords, queue):
    """
    Шукає ключові слова у файлах та додає результати до черги.
    :param file_list: Список файлів для обробки
    :param keywords: Список ключових слів
    :param queue: Черга для збереження результатів
    """
    results = defaultdict(list)

    for file_path in file_list:
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()
                for keyword in keywords:
                    if keyword in content:
                        results[keyword].append(os.path.basename(file_path))
        except (FileNotFoundError, PermissionError, IOError) as e:
            logging.error(f"{Fore.RED}Помилка обробки файлу {file_path}: {e}{Style.RESET_ALL}")

    queue.put(results)


def multiprocessing_search(directory, keywords, num_processes=4):
    """
    Виконує пошук ключових слів у файлах, використовуючи multiprocessing.
    :param directory: Папка з файлами
    :param keywords: Список ключових слів
    :param num_processes: Кількість процесів
    :return: Словник знайдених слів у файлах
    """
    files = [
        os.path.join(directory, f)
        for f in os.listdir(directory)
        if os.path.isfile(os.path.join(directory, f))
    ]

    queue = Queue()
    processes = []
    chunk_size = len(files) // num_processes
    file_chunks = [files[i:i + chunk_size] for i in range(0, len(files), chunk_size)]

    for chunk in file_chunks:
        process = Process(target=search_keywords_in_files, args=(chunk, keywords, queue))
        processes.append(process)
        process.start()

    for process in tqdm(processes, desc=f"{Fore.CYAN}Обробка файлів у процесах{Style.RESET_ALL}", ncols=80, bar_format="{l_bar}{bar} {n_fmt}/{total_fmt}"):
        process.join()

    results = defaultdict(list)
    while not queue.empty():
        result = queue.get()
        for key, paths in result.items():
            results[key].extend(paths)

    return results


def main():
    """
    Головна функція для запуску пошуку слів у багатопроцесному режимі.
    """
    clear_console()

    keywords = generate_keywords()
    print(f"{Fore.BLUE}Згенеровані ключові слова для пошуку: {', '.join(keywords)}{Style.RESET_ALL}")

    start_time = time()
    results = multiprocessing_search("text_files", keywords, num_processes=4)
    end_time = time()

    # Форматування та виведення результатів у красивому вигляді
    table_data = []
    for keyword, files in results.items():
        total_files = len(files)
        displayed_files = ", ".join(files[:5]) + ("..." if total_files > 5 else "")
        table_data.append([keyword, f"{total_files} файлів знайдено", displayed_files])

    print(f"{Fore.GREEN}\nРезультати пошуку:{Style.RESET_ALL}")
    print(tabulate(table_data, headers=["Ключове слово", "Кількість файлів", "Приклади файлів"], tablefmt="grid"))
    print(f"\n{Fore.YELLOW}Час виконання:{Style.RESET_ALL} {end_time - start_time:.5f} секунд\n")


if __name__ == "__main__":
    main()
