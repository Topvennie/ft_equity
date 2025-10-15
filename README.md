# FT Equity

Makes an export to excel of every equity from Europe, the US or Canada from the [Financial Times](https://markets.ft.com/data/equities/results).

It includes the following attributes:

- Market cap
- Dividend yield
- Consensus forecast
- Price to earnings ratio
- Price to book value
- 52 week price change percentage

The excel gets saved in your downloads directory.

## How to use

Either download the correct binary from the releases or

1. Clone the repo
2. Create a virtual environment `python -m venv .venv`
3. Activate the virtual environment `source .venv/bin/activate`
4. Install the dependencies `pip install -r requirements.txt`
5. Run the program `python main.py`
