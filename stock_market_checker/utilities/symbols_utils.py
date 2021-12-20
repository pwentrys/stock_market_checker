from pathlib import Path

from config.config import FILENAME, update_symbol


def _update_data(app, ) -> bool:
    """Get data from CSV and attach data to Flask object

    Returns:
        bool: Whether data has changed since last time
    """
    cwd = Path.cwd()
    filepath = cwd.joinpath(FILENAME)
    text_raw = filepath.read_text(encoding='utf=8')
    if app.TEXT_LAST == text_raw:
        # print(f'Last = Current')
        return False

    app.TEXT_LAST = text_raw
    text_split = text_raw.splitlines()
    data_dict = {}
    for line in text_split:
        line = line.split(',')

        symbol = line[0]
        value = line[1]

        data_dict.update({symbol: value})

    app.DATA = data_dict
    return True


def update_app_symbols(app):
    app.SYMBOLS = update_symbol()


def symbols_path_get():
    return Path.cwd().joinpath('static').joinpath('symbols.ini')


def symbols_get():
    # Grab symbols from ini file
    symbols_path = symbols_path_get()
    symbols_full = symbols_path.read_text(encoding='utf-8')
    symbols_list = symbols_full.splitlines()

    return symbols_list


def symbols_add(symbol: str, app) -> bool:
    symbols = symbols_get()
    symbol = symbol.upper()
    if symbol not in symbols:
        symbols.append(symbol)
        symbols = sorted(symbols)
        symbols_out = '\n'.join(symbol for symbol in symbols)
        symbols_path_get().write_text(symbols_out, encoding='utf-8')
        _update_data(app=app)
        update_app_symbols(app=app)
        return True
    return False


def symbols_remove(symbol: str, app) -> bool:
    symbols = symbols_get()
    symbol = symbol.upper()
    if symbol in symbols:
        symbols.remove(symbol)
        symbols = sorted(symbols)
        symbols_out = '\n'.join(symbol for symbol in symbols)
        symbols_path_get().write_text(symbols_out, encoding='utf-8')
        _update_data(app=app)
        update_app_symbols(app=app)
        return True
    return False


def symbols_update(socketio):
    socketio.emit('symbols_update', json={'data': 'symbols_update'})
