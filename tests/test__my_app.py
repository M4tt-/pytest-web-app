#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May 15 13:58:22 2022

:author: mrunyon

Description
-----------

This module contains a series of testcases using the Pytest
framework in Python to test that the server-client application works as
expected. In particular, we:

   - Launch a server and 2 clients in an automated way
   - Execute some number of tests
   - Teardown the clients and server in an automated way

The setup and teardown are implemented with pytest fixtures.
The server is launched in a separate process.
The config is sourced from either ENV or command line arg:
    - Sourcing from $APP_TEST_CONFIG takes priority.
    - If $APP_TEST_CONFIG undefined, any --conf option is used.
    - If $APP_TEST_CONFIG undefined + no --conf option, defaults.

Tested with Python 3.6.6 on Ubuntu 18.04.6 LTS.

Usage
-----

Navigate to base path of the repo, i.e., the directory before 'app', etc.,
and execute the following command in terminal:

    $export APP_TEST_CONFIG="</path/to/.json>"
    $pytest tests/test__my_app.py [pytest_opts]

                         or

    $pytest tests/test__my_app.py [--conf <conf_opt>] [pytest_opts]

                        or

    $pytest tests/test__my_app.py [pytest_opts]

Recommended pytest_opts:

    $pytest tests/test__my_app.py -W ignore::DeprecationWarning -v
"""

# %% IMPORTS
import json
import os
from multiprocessing import Process
from pathlib import Path
import pytest
import sys
sys.path.append('app')
import time

from hosts.client import Client
from hosts.server import MyApp
from utils.enums import Event

# %% CONSTANTS

ENV_VAR_CONFIG = 'APP_TEST_CONFIG'
PROCESS_INIT_DELAY = 0.05       # seconds
PROCESS_KILL_DELAY = 0.05       # seconds

# %% TEST FIXTURES

@pytest.fixture(scope='session')
def config_file(conf):
    """The sourced config as json."""

    try:
        env_var = os.environ[ENV_VAR_CONFIG]
    except KeyError:
        env_var = conf

    with open(env_var) as file:
        config_json = json.load(file)
    return config_json

@pytest.fixture(scope='session')
def log_file(config_file):
    """Return a unique (timestamped), guaranteed-to-exist log file Path obj."""

    path = Path(config_file.get('log'))
    new_path = path.parent / time.strftime("%Y%m%d%H%M%S", time.localtime())
    new_path.mkdir(parents=True)
    return new_path / path.name

@pytest.fixture(scope='session')
def client1(config_file, log_file):
    """First Client obj to use for testing."""

    return Client(config_file.get('server'),
                  config_file.get('port'),
                  log_file)

@pytest.fixture(scope='session')
def client2(config_file, log_file):
    """Second Client obj to use for testing."""

    return Client(config_file.get('server'),
                  config_file.get('port'),
                  log_file)

@pytest.fixture(scope='session')
def my_app(config_file, log_file):
    """MyApp obj (server) to use for testing."""

    return MyApp(config_file.get('server'),
                 config_file.get('port'),
                 log_file)

@pytest.fixture(autouse=True, scope='session')
def server_process(my_app):
    """Server process object complete with teardown procedure."""

    server_process = Process(target=my_app.run, daemon=True)
    server_process.start()
    time.sleep(PROCESS_INIT_DELAY)
    yield server_process
    try:
        server_process.kill()
    except AttributeError:
        server_process.terminate()
    time.sleep(PROCESS_KILL_DELAY)
    #server_process.close()

# %% TEST CLASSES


class TestClient:
    """Test class for the Client class."""

    def test_01_client1_server_check(self, client1, config_file):
        """Verify a client gets the correct server (config check)."""

        assert config_file.get('server') == client1._Client__server

    def test_02_client1_port_check(self, client1, config_file):
        """Verify a client gets the correct port (config check)."""

        assert config_file.get('port') == client1._Client__port

    def test_03_client1_read_count(self, client1):
        """Verify the first client has sent the correct # of requests."""

        client1.send()
        assert client1.get() == client1._Client__EVENTS

    def test_04_client2_cumulative_read_count(self, client2):
        """Verify the second client has sent the correct # of requests."""

        client2.send()
        assert client2.get() == 2*client2._Client__EVENTS

    def test_05_client_logging_count(self, client1, log_file):
        """Verify client logged correct # of events (client log integrity)."""

        with open(log_file, 'r') as file:
            clnt_lines = [line for line in file.readlines() if '-' not in line]
        assert len(clnt_lines) == 2*client1._Client__EVENTS


class TestMyApp:
    """Test class for the MyApp."""

    def test_01_server_check(self, my_app, config_file):
        """Verify MyApp gets the correct host (config check)."""

        assert config_file.get('server') == my_app._MyApp__host

    def test_02_server_port_check(self, my_app, config_file):
        """Verify MyApp gets the correct port (config check)."""

        assert config_file.get('port') == my_app._MyApp__port

    @pytest.mark.xfail(reason="Server misses last ~15 event logs from client2.")
    def test_03_log_file_server_logging(self, client1, log_file):
        """Verify server logged correct # of events (server log integrity)."""

        with open(log_file, 'r') as file:
            srv_lines = [line for line in file.readlines() if '-' in line]
        assert len(srv_lines) == 2*client1._Client__EVENTS


class TestEvents:
    """Test class for specific event types."""

    def test_01_log_file_event_type_check(self, log_file):
        """Verify each logged event is of an expected type (data integrity)."""

        valid_events = list(Event)
        with open(log_file, 'r') as file:
            for line in file.readlines():
                assert any(event in line for event in valid_events)
