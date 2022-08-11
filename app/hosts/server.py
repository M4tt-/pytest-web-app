import sys
import logging

from flask import request, Flask
from utils.enums import Event

_logger = logging.getLogger(__name__)
logging.getLogger('werkzeug').setLevel(logging.ERROR)

sys.modules['flask.cli'].show_server_banner = lambda *x: None


class MyApp:
    def __init__(self, host: str, port: int, log: str):
        self.__host = host
        self.__port = port
        self.__app = Flask('myapp')

        self.__events_file = open(log, 'a+')
        self.__app.add_url_rule(rule = '/events', methods = ['GET', 'POST'], view_func = self.__events)

        self.__events = {}

    def run(self):
        _logger.info('Starting server...')
        self.__app.run(host = self.__host, port = self.__port)

    def __update(self, host: str, event: str):
        self.__events.setdefault(host, {})
        self.__events[host].setdefault(event, 0)
        self.__events[host][event] += 1

    def __events(self):
        if request.method in ['GET']:
            event_type = request.args.get('event')

            if event_type and event_type.lower() not in [ev for ev in Event]:
                return 'Invalid event type!', 400

            events = self.__events.get(request.remote_addr, {})
            if events:
                if event_type is None:
                    count = sum(self.__events[request.remote_addr].values())
                else:
                    count = events.get(event_type, 0)
                return {'Events' if event_type is None else event_type: count}
            else:
                return f'No events recorded for {request.remote_addr}'

        if request.method in ['POST']:
            event_data = request.get_data(as_text = True)

            if not event_data:
                return 'Invalid event type or format!', 400

            event_type, message = event_data.split(':', maxsplit = 1)
            if event_type.strip().lower() not in [ev.lower() for ev in Event]:
                return 'Invalid event type or format!', 400

            self.__update(request.remote_addr, event_type)
            self.__events_file.write(f'{request.remote_addr} - {event_data}\n')

            return {'msg': f'Event from {request.remote_addr} logged'}

    def stop(self):
        self.__events_file.close()
        _logger.info('Server stopped')
