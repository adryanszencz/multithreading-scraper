# Multithreading Web Scraper

Projeto do módulo de **Python Avançado** da EBAC (Profissão: Desenvolvedor Full Stack Python).

**Autor:** Adryan Szenczuk

Scraper que baixa a lista de filmes populares de um catálogo, entra na página de cada filme e grava
título, data de lançamento, nota e sinopse em `movies.csv`. A extração roda duas vezes, com **1 thread**
e com um **pool de threads** (`concurrent.futures.ThreadPoolExecutor`), para comparar o tempo.

> O catálogo usado é o site de exemplo do professor (havokkmorands.github.io/movie-catalog), porque o
> IMDb muda a estrutura com frequência e bloqueia scrapers.

## Tecnologias

- Python 3
- requests
- BeautifulSoup (bs4)
- concurrent.futures / threading

## Como rodar

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows (no Linux/macOS: source .venv/bin/activate)
pip install -r requirements.txt
python multithreading.py              # MAX_THREADS = 10
python multithreading.py --threads 20 # testa outra quantidade de threads
```

O número de threads usado é `min(MAX_THREADS, quantidade de filmes)`: não adianta abrir 20 threads para 5 filmes.

## Resultado (30 filmes)

| Threads | 1 thread | Com threads | Ganho |
|---------|----------|-------------|-------|
| 5       | 11,45 s  | 0,97 s      | 11,8x |
| 10      | 4,89 s   | 0,56 s      | 8,8x  |
| 20      | 4,59 s   | 0,41 s      | 11,2x |

Como o trabalho é quase todo espera de rede (I/O), as threads ficam esperando em paralelo e o tempo total cai muito.
O arquivo `movies.csv` deste repositório é a saída de uma execução.
