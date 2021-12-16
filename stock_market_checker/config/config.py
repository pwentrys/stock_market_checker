BASE_URL = 'https://www.google.com/finance/quote'

CURRENCY = '$'

FILENAME = 'output.csv'

HOST_ADDRESS = '0.0.0.0'
HOST_PORT = 1337
HOST_UPDATE_PATH = 'update_data'

DATA_UPDATE_INTERVAL = 10.0

# Grab symbols from ini file
from pathlib import Path


def update_symbol():
    cwd = Path.cwd()
    symbols_path = cwd.joinpath('static').joinpath('symbols.ini')
    symbols_full = symbols_path.read_text(encoding='utf-8')
    symbols_list = symbols_full.splitlines()
    return symbols_list
