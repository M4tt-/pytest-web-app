import json
import logging
import argparse

from hosts.server import MyApp
from hosts.client import Client


logging.basicConfig(
    format = '%(asctime)s - %(levelname)s - %(message)s',
    level = logging.INFO
)
_logger = logging.getLogger(__name__)


def main(args: argparse.Namespace):
    """
    :param args:
    :return:
    """
    with open('config.json') as file:
        config = json.load(file)

    if args.mode in ['server']:
        app = None
        try:
            app = MyApp(config.get('server'), config.get('port'), log = config.get('log'))
            app.run()
        except Exception:
            _logger.info(f'Shutting down {config.get("server")}')
        finally:
            if app:
                app.stop()
    else:
        client = Client(config.get('server'), config.get('port'), log = config.get('log'))
        client.send()
        count = client.get()
        _logger.info(f'Server logged {count} events')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description = 'My Server-Client App'
    )
    parser.add_argument(
        dest = 'mode',
        choices = ['server', 'client'],
        help = 'Set the App to be in Client or Server mode'
    )
    args = parser.parse_args()

    main(args)
