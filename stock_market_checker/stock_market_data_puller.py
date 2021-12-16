import concurrent.futures
import os
import time
import urllib.request
from pathlib import Path

import requests as requests
from bs4 import BeautifulSoup

from config.config import BASE_URL, CURRENCY, FILENAME, HOST_ADDRESS, HOST_PORT, HOST_UPDATE_PATH, SYMBOLS


def _format_div_text(text: str, currency: str = '$') -> str:
    """Remove currency from text

    Args:
        text (str): div text with currency symbol

    Returns:
        str: Formatted text
    """
    text = text.replace(currency, '')
    text = text.replace(',', '')
    return text


def _run_single(symbol: str) -> str:
    """

    Args:
        symbol (str): Single ticket symbol to run

    Returns:
        str: USD price
    """
    url = f'{BASE_URL}/{symbol}'
    req = requests.get(
        url=url,
    )

    html = req.text
    soup = BeautifulSoup(html, 'html5lib')
    divs = soup.findAll('div')
    texts_out = []
    i = 0

    text_out = 'ERROR'
    for div in divs:
        text = div.getText()
        if CURRENCY in text:
            text = _format_div_text(text, CURRENCY)
            texts_out.append(text)
            i += 1
            if i == 11:
                text_out = text
                break

    shortest_text = 'A' * 50
    for text in texts_out:
        if len(text) < len(shortest_text):
            shortest_text = text

    if text_out == shortest_text:
        return text_out.format('{:.2f}')
    else:
        return '0.00'.format('{:.2f}')


def load_url(symbol, timeout):
    url = f'{BASE_URL}/{symbol}'
    with urllib.request.urlopen(url, timeout=timeout) as conn:
        return conn.read()


def write_csv(data: dict):
    """Write CSV

    Args:
        data (dict): Symbol to dollar value dictionary.

    Returns:
        bool: Success or fail bool
    """
    string_list = []
    for k, v in data.items():
        # v = v[:-1]
        # v = f'{v}{randint(0, 9)}'
        string_list.append(f'{k},{v}')

    output = '\n'.join(string_list)

    cwd = Path.cwd()
    filepath = cwd.joinpath(FILENAME)
    filepath.write_text(output, encoding='utf-8')

    requests.post(f'http://{HOST_ADDRESS}:{HOST_PORT}/{HOST_UPDATE_PATH}')


def _run_all() -> dict:
    dict_res = {}
    with concurrent.futures.ProcessPoolExecutor(max_workers=os.cpu_count() * 2) as executor:
        future_to_url = {executor.submit(_run_single, symbol): symbol for symbol in SYMBOLS}
        for future in concurrent.futures.as_completed(future_to_url):
            symbol = future_to_url[future]
            try:
                value = future.result()
            except Exception as exc:
                print('%r generated an exception: %s' % (symbol, exc))
            else:
                dict_res.update({symbol: value})

    dict_out = dict(sorted(dict_res.items()))

    return dict_out


def run() -> dict:
    dict_out = _run_all()
    # pp(dict_out)

    write_csv(data=dict_out)

    return dict_out


if __name__ == '__main__':
    while True:
        start_time = time.time()
        run()
        end_time = time.time()
        difference_time = end_time - start_time
        print(difference_time)
        time.sleep(10.0 - difference_time)
