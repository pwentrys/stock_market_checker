import concurrent.futures
import os
import time
import urllib.request
from pathlib import Path

import requests as requests
from bs4 import BeautifulSoup

from config.config import (
    BASE_URL, CURRENCY, DATA_UPDATE_INTERVAL, FILENAME, HOST_ADDRESS, HOST_PORT, HOST_UPDATE_PATH,
    update_symbol
)


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


def validate_value(value: str) -> bool:
    """Ensure value is valid

    Args:
        value (str): Value string

    Returns:
        bool: Whether value is valid or not.
    """
    if len(value) < 4:
        return False
    if '%' in value:
        return False
    if '.' not in value:
        return False
    if (len(value) - 3) != value.index('.'):
        return False

    return True


def _run_all() -> dict:
    dict_res = {}
    with concurrent.futures.ProcessPoolExecutor(max_workers=os.cpu_count() * 2) as executor:
        future_to_url = {executor.submit(_run_single, symbol): symbol for symbol in update_symbol()}
        for future in concurrent.futures.as_completed(future_to_url):
            symbol = future_to_url[future]
            try:
                value = future.result()
            except Exception as exc:
                print('%r generated an exception: %s' % (symbol, exc))
            else:
                if validate_value(value):
                    dict_res.update({symbol: value})
                else:
                    print(f'Value {symbol} is invalid.')

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
        try:
            run()
        except Exception as e:
            print(e)
        finally:
            end_time = time.time()
            difference_time = end_time - start_time
            # print(difference_time)
            run_difference = DATA_UPDATE_INTERVAL - difference_time
            if run_difference < DATA_UPDATE_INTERVAL:
                run_difference = DATA_UPDATE_INTERVAL
            time.sleep(run_difference)
