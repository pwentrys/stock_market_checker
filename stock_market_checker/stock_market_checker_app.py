from pathlib import Path
from uuid import uuid4

from flask import Flask, jsonify, render_template
from flask_socketio import SocketIO

from config.config import BASE_URL, FILENAME, HOST_ADDRESS, HOST_PORT

# Initial app start config - Flask object defines
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


def _update_data() -> bool:
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


@app.route('/')
def index():
    """Main landing page

    Returns:
        flask.render_template: Renders template for index.html
    """
    return render_template('index.html', data=app.DATA, base_url=BASE_URL)


@app.route('/update_data', methods=['POST'])
def update_data():
    """Update data endpoint which ultimately updates data using the output csv

    Returns:
        int: Returns status 200 for success
    """
    resp = _update_data()

    if resp:
        json_data = jsonify(app.DATA)
        server_update(json_data)

    resp_out = jsonify(success=resp)
    return resp_out


@socketio.on('connected')
def handle_connected_event(json):
    """Debug for each time client place connects.

    Args:
        json (json): Data dict from client.

    Returns:
        None
    """
    print('received json: ' + str(json))


def server_update(json):
    """Handles server updates

    Args:
        json ():

    Returns:

    """
    json_data = json.json
    # print('updated server json: ' + str(json_data))
    socketio.emit('client_update', json_data)


@app.route('/<path:the_path>')
def all_other_routes(the_path):
    return app.send_static_file(the_path)


if __name__ == '__main__':
    _update_data()
    socketio.run(
        app,
        host=HOST_ADDRESS,
        port=HOST_PORT,
    )
