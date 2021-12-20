from uuid import uuid4

from flask import Flask, jsonify, redirect, render_template
from flask_socketio import SocketIO

from config.config import BASE_URL, HOST_ADDRESS, HOST_PORT
# Initial app start config - Flask object defines
from utilities.symbols_utils import _update_data, symbols_add, symbols_remove, symbols_update, update_app_symbols

server_options = {
    'async_mode': 'threading',
}
app = Flask(
    __name__,
)
app.DATA = {'Symbol': 'Value'}
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = str(uuid4())
socketio = SocketIO(
    app,
    server_options=server_options,
)

app.TEXT_LAST = ''
app.SYMBOLS = []
update_app_symbols(app)

HEAD_HTML = """
    <meta charset="UTF-8">
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <link href="main.css" rel="stylesheet">
    """

FOOTER_HTML = """
    <script crossorigin="anonymous"
            integrity="sha512-q/dWJ3kcmjBLU4Qc47E4A9kTB4m3wuTY7vkFJDTZKjTs8jhyGQnaUrxa0Ytd0ssMZhbNua9hE+E7Qv1j+DyZwA=="
            src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
    """


@app.route('/')
def index():
    """Main landing page

    Returns:
        flask.render_template: Renders template for index.html
    """
    return render_template(
        'index.html',
        title='Stocks Main',
        data=app.DATA,
        base_url=BASE_URL,
        head_html=HEAD_HTML,
        footer_html=FOOTER_HTML
    )


def reload_page():
    socketio.emit('reload_page', json={'data': 'reload_page'})


@app.route('/symbols/<string:action>/<string:symbol>')
def symbols_action(action: str, symbol: str):
    # alert_message = ''
    match action:
        case 'add':
            symbols_add(symbol=symbol, app=app)
            reload_page()
            symbols_update(socketio=socketio)
            # alert_message = f'Added: {symbol.upper()}'
        case 'remove':
            symbols_remove(symbol=symbol, app=app)
            reload_page()
            symbols_update(socketio=socketio)
            # alert_message = f'Removed: {symbol.upper()}'
        case _:
            # alert_message = f'ERROR: {symbol.upper()}'
            print('ERROR')

    return redirect(f'http://{HOST_ADDRESS}:{HOST_PORT}/symbols')


@app.route('/symbols')
def symbols():
    """Symbols management page

    Returns:
        flask.render_template: Renders template for symbols.html
    """
    symbols = app.SYMBOLS
    alert_message = ''
    return render_template(
        'symbols.html',
        title='Symbols Management',
        head_html=HEAD_HTML,
        footer_html=FOOTER_HTML,
        symbols=symbols,
        alert_message=alert_message,
        symbols_url=f'http://{HOST_ADDRESS}:{HOST_PORT}/symbols'
    )


@app.route('/update_data', methods=['POST'])
def update_data():
    """Update data endpoint which ultimately updates data using the output csv

    Returns:
        int: Returns status 200 for success
    """
    resp = _update_data(app=app)

    if resp:
        json_data = jsonify(app.DATA)
        server_update(json_data)

    resp_out = jsonify(success=resp)
    return resp_out


@socketio.on('connect')
def handle_connect_event():
    """Debug for each time client place connects.

    Returns:
        None
    """
    print(f'Automated Connect Event')


@socketio.on('connected')
def handle_connected_event(json=None):
    """Debug for each time client place connects.

    Args:
        json (json): Data dict from client.

    Returns:
        None
    """
    print(f'Connect Event: {json}')


@socketio.on('disconnect')
def handle_disconnect_event():
    """Debug for each time client place disconnects.

    Returns:
        None
    """
    print(f'Automated Disconnect Event')


@socketio.on('disconnected')
def handle_disconnected_event(json=None):
    """Debug for each time client place disconnects.

    TODO: Figure out how this can work.

    Args:
        json (json): Data dict from client.

    Returns:
        None
    """
    print(f'Disconnect Event: {json}')


def server_update(json):
    """Handles server updates

    Args:
        json (): Json data.

    Returns:

    """
    json_data = json.json
    # print('updated server json: ' + str(json_data))
    socketio.emit('client_update', json_data)


@app.route('/<path:the_path>')
def all_other_routes(the_path):
    return app.send_static_file(the_path)


if __name__ == '__main__':
    _update_data(app=app)
    socketio.run(
        app,
        host=HOST_ADDRESS,
        port=HOST_PORT,
    )
