"""Web scraper de filmes com multithreading (Exercício Módulo 4, Python Avançado - EBAC).

Baixa a lista de filmes populares do catálogo de exemplo do curso, entra no
detalhe de cada filme e grava título, lançamento, nota e sinopse em movies.csv.
Roda a extração duas vezes, com 1 thread e com várias threads, e compara o tempo.

Uso:
    python multithreading.py              # MAX_THREADS = 10
    python multithreading.py --threads 20
"""
import argparse
import concurrent.futures
import csv
import random
import threading
import time

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://havokkmorands.github.io/"
POPULAR_MOVIES_URL = BASE_URL + "movie-catalog/"
CSV_FILE = "movies.csv"

# headers que simulam um navegador (Mozilla/Chrome)
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

MAX_THREADS = 10

# várias threads escrevem no mesmo CSV, então a escrita é protegida por um lock
csv_lock = threading.Lock()


def get_text(container, test_id, prefix=""):
    tag = container.find(attrs={"data-testid": test_id})
    if tag is None:
        return None
    return tag.get_text(strip=True).replace(prefix, "").strip()


def extract_movie_details(movie_link):
    """Entra na página de um filme e devolve [título, lançamento, nota, sinopse]."""
    time.sleep(random.uniform(0, 0.2))
    response = requests.get(movie_link, headers=headers, timeout=20)
    movie_soup = BeautifulSoup(response.content, "html.parser")

    detail = movie_soup.find("section", attrs={"data-testid": "movie-detail"})
    if detail is None:
        print(f"Detalhe do filme não encontrado: {movie_link}")
        return None

    title = get_text(detail, "movie-title")
    date = get_text(detail, "movie-release", "Lançamento:")
    rating = get_text(detail, "movie-rating", "Nota:")
    plot_text = get_text(detail, "movie-synopsis", "Sinopse:")

    if not all([title, date, rating, plot_text]):
        return None

    row = [title, date, rating, plot_text]
    with csv_lock:
        with open(CSV_FILE, mode="a", newline="", encoding="utf-8") as file:
            csv.writer(file).writerow(row)
    print(f"[{threading.current_thread().name}] {title} ({date}) nota {rating}")
    return row


def extract_movie_links(soup):
    """Lê a página da lista e devolve os links de detalhe de cada filme."""
    container = soup.find("section", attrs={"data-testid": "movies-list"})
    if container is None:
        print("Container principal não encontrado.")
        return []

    links = []
    for movie in container.find_all("article", attrs={"data-testid": "movie-item"}):
        a_tag = movie.find("a", attrs={"data-testid": "movie-link"}, href=True)
        if a_tag:
            links.append(BASE_URL + a_tag["href"].lstrip("/"))
    return links


def reset_csv():
    with open(CSV_FILE, mode="w", newline="", encoding="utf-8") as file:
        csv.writer(file).writerow(["title", "release_date", "rating", "synopsis"])


def extract_single_thread(movie_links):
    """Versão sequencial: um filme de cada vez, numa thread só."""
    for link in movie_links:
        extract_movie_details(link)


def extract_multithread(movie_links, max_threads):
    """Versão concorrente: um pool com min(max_threads, nº de filmes) threads."""
    threads = min(max_threads, len(movie_links))
    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        list(executor.map(extract_movie_details, movie_links))
    return threads


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--threads", type=int, default=MAX_THREADS)
    args = parser.parse_args()

    response = requests.get(POPULAR_MOVIES_URL, headers=headers, timeout=20)
    print("Status:", response.status_code)
    movie_links = extract_movie_links(BeautifulSoup(response.content, "html.parser"))
    print(f"{len(movie_links)} filmes encontrados\n")
    if not movie_links:
        return

    print("== 1 thread")
    reset_csv()
    start = time.time()
    extract_single_thread(movie_links)
    single_time = time.time() - start

    print(f"\n== multithreading (MAX_THREADS = {args.threads})")
    reset_csv()  # o CSV final é o da versão com threads
    start = time.time()
    used = extract_multithread(movie_links, args.threads)
    multi_time = time.time() - start

    print("\n== Comparativo")
    print(f"1 thread:          {single_time:.2f} s")
    print(f"{used} threads:        {multi_time:.2f} s")
    print(f"Ganho:             {single_time / multi_time:.1f}x mais rápido")


if __name__ == "__main__":
    main()
