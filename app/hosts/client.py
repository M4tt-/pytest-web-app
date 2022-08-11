import time
import random
import logging
import requests

from utils.enums import Event

_logger = logging.getLogger(__name__)


class Client:
    __EVENTS = 1000

    def __init__(self, server: str, port: int, log: str):
        self.__server = server
        self.__port = port
        self.__events_file = log

    def send(self):
        events = [e for e in Event]
        _logger.info(f'Sending {Client.__EVENTS} events...')
        with open(self.__events_file, 'a+') as file:
            for event in range(Client.__EVENTS):
                event_type = random.choice(events)
                event_data = f'{event_type}: This is event {event}'

                _ = requests.post(f'http://{self.__server}:{self.__port}/events', data = event_data)
                _ = file.write(f'{event_data}\n')
                time.sleep(.01)

    def get(self):
        resp = requests.get(f'http://{self.__server}:{self.__port}/events')
        return resp.json().get('Events')

