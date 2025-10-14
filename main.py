import concurrent.futures
import threading

from equity import Equity
from excel import export_excel
from request import get_equity, get_pages
from datetime import datetime
from tqdm import tqdm
import pytz

THREADS = 128


def get_all_equities() -> list[Equity]:
    total_pages = get_pages()

    all_equities: list[Equity] = []
    lock = threading.Lock()

    def worker(page: int) -> list[Equity]:
        equities = get_equity(page)

        return equities

    with concurrent.futures.ThreadPoolExecutor(max_workers=THREADS) as executor:
        futures = {
            executor.submit(worker, page): page for page in range(1, total_pages + 1)
        }

        with tqdm(total=total_pages, desc="Pagina's bekijken", ncols=90) as pbar:
            for fut in concurrent.futures.as_completed(futures):
                page = futures[fut]
                try:
                    equities = fut.result()
                    with lock:
                        all_equities.extend(equities)
                except Exception as e:
                    print(f"[!] Error fetching page {page}: {e}")
                finally:
                    pbar.update(1)

    return all_equities


def main():
    print("Alle data verzamelen")
    equities = get_all_equities()

    print("Omzetten naar een excel")
    brussels_tz = pytz.timezone("Europe/Brussels")
    now = datetime.now(brussels_tz)
    timestamp = now.strftime("%Y-%m-%d_%H:%M")

    export_excel(equities, f"equities_{timestamp}.xlsx")


if __name__ == "__main__":
    main()
