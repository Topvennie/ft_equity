import xlsxwriter

from equity import Equity


def export_excel(equities: list[Equity], filename: str):
    workbook = xlsxwriter.Workbook(filename)
    worksheet = workbook.add_worksheet("Equities")

    headers = [
        "Name",
        "Ticker",
        "Country",
        "Sector",
        "Industry",
        "Market Cap",
        "Dividend Yield (%)",
        "Consensus Forecast",
        "Price to Earnings Ratio",
        "Price to Book Value (MRQ)",
        "52 Week Price Change (%)",
    ]
    worksheet.write_row(0, 0, headers)

    number_format = workbook.add_format({"num_format": "#,##0.00"})

    for row_idx, eq in enumerate(equities, start=1):
        worksheet.write(row_idx, 0, eq.name)
        worksheet.write(row_idx, 1, eq.ticker)
        worksheet.write(row_idx, 2, eq.country)
        worksheet.write(row_idx, 3, eq.sector)
        worksheet.write(row_idx, 4, eq.industry)
        if eq.market_cap:
            worksheet.write_number(row_idx, 5, eq.market_cap, number_format)
        if eq.dividend:
            worksheet.write_number(row_idx, 6, eq.dividend, number_format)
        worksheet.write(row_idx, 7, eq.consensus)
        if eq.price_to_earning:
            worksheet.write_number(row_idx, 8, eq.price_to_earning, number_format)
        if eq.price_to_book:
            worksheet.write_number(row_idx, 9, eq.price_to_book, number_format)
        if eq.week_price_change:
            worksheet.write_number(
                row_idx,
                10,
                eq.week_price_change,
                number_format,
            )

    last_row = len(equities)
    last_col = len(headers) - 1
    worksheet.autofilter(0, 0, last_row, last_col)

    worksheet.set_column(0, 0, 35)
    worksheet.set_column(1, 1, 12)
    worksheet.set_column(2, 4, 20)
    worksheet.set_column(5, 10, 18)

    workbook.close()
