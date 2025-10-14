import re
from bs4 import BeautifulSoup
import html
import requests
import json

from equity import Equity

URL = "https://markets.ft.com/data/equities/ajax/updateScreenerResults"

PAYLOAD = {
    "data": json.dumps(
        [
            {
                "ArgsOperator": None,
                "ValueOperator": None,
                "Arguments": [],
                "Clauses": [
                    {
                        "Operator": 4,
                        "Values": [
                            "AT",
                            "BE",
                            "BG",
                            "CZ",
                            "DK",
                            "EE",
                            "FI",
                            "FR",
                            "DE",
                            "GR",
                            "HU",
                            "IS",
                            "IE",
                            "IT",
                            "LT",
                            "NL",
                            "NO",
                            "PL",
                            "PT",
                            "RO",
                            "SI",
                            "ES",
                            "SE",
                            "CH",
                            "UA",
                            "GB",
                            "CA",
                            "US",
                        ],
                    }
                ],
                "ClauseGroups": [],
                "Field": "RCCCountryCode",
                "Identifiers": None,
                "Style": None,
            },
            {
                "ArgsOperator": None,
                "ValueOperator": None,
                "Arguments": [],
                "Clauses": [],
                "ClauseGroups": [],
                "Field": "RCCICBSectorCode",
                "Identifiers": None,
                "Style": None,
            },
            {
                "ArgsOperator": None,
                "ValueOperator": None,
                "Arguments": [],
                "Clauses": [],
                "ClauseGroups": [],
                "Field": "RCCICBIndustryCode",
                "Identifiers": None,
                "Style": None,
            },
            {
                "ArgsOperator": None,
                "ValueOperator": None,
                "Arguments": [],
                "Clauses": [],
                "ClauseGroups": [],
                "Field": "RCCMarketCap",
                "Identifiers": None,
                "Style": None,
            },
            {
                "ArgsOperator": None,
                "ValueOperator": None,
                "Arguments": [],
                "Clauses": [],
                "ClauseGroups": [],
                "Field": "RCCDividendYield",
                "Identifiers": None,
                "Style": None,
            },
            {
                "ArgsOperator": None,
                "ValueOperator": None,
                "Arguments": [],
                "Clauses": [
                    {"Operator": 4, "Values": ["BUY", "STRONG BUY"]},
                    {"Operator": 4, "Values": ["OUTPERFORM"]},
                    {"Operator": 4, "Values": ["HOLD"]},
                    {"Operator": 4, "Values": ["SELL"]},
                    {"Operator": 4, "Values": ["STRONG SELL"]},
                    {"Operator": 4, "Values": ["NORATING"]},
                ],
                "ClauseGroups": [],
                "Field": "RCCConsensusRecommendationv2",
                "Identifiers": None,
                "Style": None,
            },
            {
                "ArgsOperator": None,
                "ValueOperator": None,
                "Arguments": [],
                "Clauses": [],
                "ClauseGroups": [],
                "Field": "RCCPEExclXItemsTTM",
                "Identifiers": None,
                "Style": None,
            },
            {
                "ArgsOperator": None,
                "ValueOperator": None,
                "Arguments": [],
                "Clauses": [],
                "ClauseGroups": [],
                "Field": "RCCPriceToBookMRQ",
                "Identifiers": None,
                "Style": None,
            },
            {
                "ArgsOperator": None,
                "ValueOperator": None,
                "Arguments": [],
                "Clauses": [],
                "ClauseGroups": [],
                "Field": "RCCPrice52wPctChg",
                "Identifiers": None,
                "Style": None,
            },
        ]
    ),
    "currencyCode": "EUR",
    "sort": json.dumps({"field": "RCCFTStandardName", "direction": "ascending"}),
}

HEADERS = {"Content-Type": "application/x-www-form-urlencoded"}


def send_request(data: dict) -> str:
    """
    The returned boolean value indicates if there are any pages left
    """

    for attempt in range(5):
        try:
            resp = requests.post(URL, headers=HEADERS, data=data, timeout=20)
            if resp.status_code != 200:
                raise Exception(f"Status code {resp.status_code}")

            data = resp.json()
            html = data.get("html", "")

            return html

        except Exception as e:
            if attempt < 4:
                continue
            else:
                raise Exception(
                    f"Er is iets misgegaan tijdens het maken van de request: {e}"
                )

    return ""


def get_equity(page: int) -> list[Equity]:
    local_payload = PAYLOAD.copy()
    local_payload["page"] = str(page)

    try:
        html = send_request(local_payload)
    except Exception as e:
        print(e)
        return []

    if "No matches found" in html:
        return []

    equities = parse_equities_from_html(html)
    return equities


def get_pages() -> int:
    local_payload = PAYLOAD.copy()
    local_payload["page"] = "1"

    try:
        html = send_request(local_payload)
    except Exception as e:
        print(e)
        return -1

    soup = BeautifulSoup(sanitize_html(html), "html.parser")

    buttons = soup.find_all("button", attrs={"data-mod-pagination-num": True})
    if not buttons:
        return -1

    last_button = buttons[-1]
    attr_val = last_button.get("data-mod-pagination-num")

    if isinstance(attr_val, list):
        attr_val = attr_val[0] if attr_val else None

    try:
        return int(attr_val) if attr_val else -1
    except ValueError:
        return -1


def sanitize_html(raw_html: str) -> str:
    text = (
        raw_html.replace("\\u003c", "<")
        .replace("\\u003e", ">")
        .replace("\\u0026quot;", '"')
        .replace('\\"', '"')
        .replace("\\u0026amp;", "&")
    )

    return html.unescape(text)


def parse_market_value(value: str) -> float | None:
    value = value.strip().lower()

    if value in ("--", "", "n/a"):
        return None

    match = re.match(r"([\d.,]+)\s*([mbk]?)", value)
    if not match:
        return None

    num = float(match.group(1).replace(",", ""))
    unit = match.group(2)

    if unit == "m":
        num *= 1_000_000
    elif unit == "b":
        num *= 1_000_000_000
    elif unit == "k":
        num *= 1_000

    return num


def parse_optional_float(value: str) -> float | None:
    value = value.strip().replace("%", "")
    if value in ("--", "", "n/a"):
        return None

    try:
        return float(value)
    except ValueError:
        return None


def normalize_consensus(text: str) -> str:
    text = text.strip().title()
    if text in ("--", "", "Norating"):
        return ""

    return text


def parse_equities_from_html(html_text: str) -> list[Equity]:
    soup = BeautifulSoup(sanitize_html(html_text), "html.parser")

    rows = soup.find_all("tr")
    equities = []

    for row in rows:
        cols = row.find_all("td")
        if not cols or len(cols) < 10:
            continue

        link = cols[0].find("a", href=True)
        if link:
            name_span = link.find("span", class_="mod-ui-hide-xsmall")
            ticker_span = link.find("span", class_="mod-ui-hide-small-above")
            name = name_span.text.strip() if name_span else ""
            ticker = ticker_span.text.strip() if ticker_span else ""
        else:
            name, ticker = "", ""

        country = cols[1].get_text(strip=True)
        sector = cols[2].get_text(strip=True)
        industry = cols[3].get_text(strip=True)
        market_cap = parse_market_value(cols[4].get_text(strip=True))
        dividend_yield = parse_optional_float(cols[5].get_text(strip=True))
        consensus = normalize_consensus(cols[6].get_text(strip=True))
        price_to_earning = parse_optional_float(cols[7].get_text(strip=True))
        price_to_book = parse_optional_float(cols[8].get_text(strip=True))
        week_price_change = parse_optional_float(cols[9].get_text(strip=True))

        equities.append(
            Equity(
                name=name,
                ticker=ticker,
                country=country,
                sector=sector,
                industry=industry,
                market_cap=market_cap,
                dividend=dividend_yield,
                consensus=consensus,
                price_to_earning=price_to_earning,
                price_to_book=price_to_book,
                week_price_change=week_price_change,
            )
        )

    return equities
