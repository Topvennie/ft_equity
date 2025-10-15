import asyncio
import sys
from datetime import datetime
from pathlib import Path

import aiohttp
import pytz
from tqdm.asyncio import tqdm_asyncio

from equity import Equity
from excel import export_excel
from request import get_equity, get_pages

CONCURRENCY_LIMIT = 32


async def get_equity_with_limit(
    session: aiohttp.ClientSession, sem: asyncio.Semaphore, page: int
) -> list[Equity]:
    async with sem:
        return await get_equity(session, page)


async def get_all_equities_async() -> list[Equity]:
    connector = aiohttp.TCPConnector(limit_per_host=CONCURRENCY_LIMIT)

    async with aiohttp.ClientSession(connector=connector) as session:
        total_pages = await get_pages(session)
        if total_pages < 1:
            print("Kon het aantal pagina's niet bepalen.")
            return []

        print(f"Totaal aantal pagina's: {total_pages}")

        equities: list[Equity] = []
        sem = asyncio.Semaphore(CONCURRENCY_LIMIT)

        tasks = [
            get_equity_with_limit(session, sem, page)
            for page in range(1, total_pages + 1)
        ]

        for result in tqdm_asyncio.as_completed(
            tasks, total=total_pages, desc="Pagina's bekijken", ncols=90
        ):
            equities_page = await result
            equities.extend(equities_page)

    return equities


def get_all_equities() -> list[Equity]:
    return asyncio.run(get_all_equities_async())


def get_downloads_folder() -> Path:
    home = Path.home()
    downloads = home / "Downloads"
    if downloads.exists():
        return downloads

    return home


def main():
    print("Alle data verzamelen")
    equities = get_all_equities()

    print(f"Totaal aantal equities {len(equities)}")

    print("Omzetten naar een excel")
    brussels_tz = pytz.timezone("Europe/Brussels")
    now = datetime.now(brussels_tz)
    timestamp = now.strftime("%Y-%m-%d_%H-%M")

    filename = f"equities_{timestamp}.xlsx"
    downloads_path = get_downloads_folder()
    file_path = downloads_path / filename

    export_excel(equities, str(file_path))

    print(f"\nExcel-bestand opgeslagen als:\n{file_path}")
    print("\nDruk op Enter om het programma te sluiten...")

    try:
        input()
    except EOFError:
        pass

    sys.exit(0)


if __name__ == "__main__":
    main()
