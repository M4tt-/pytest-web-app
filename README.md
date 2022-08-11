# pytest-web-app

A show case of unit testing with `pytest` (and some `multiprocessing`).

# Requirements

- python 3.6
- flask
- requests
- Linux based OS

## Getting Started

Pull the master branch of this repository and execute the following from the
command line:

`pytest tests/test__my_app.py -W ignore::DeprecationWarning -v`

## About the App

A simple server/client application "MyApp" resides in `app` directory using
the `flask` library.

## About the Tests

A series of testcases are written using the `pytest` framework to test that the
application works as expected. The test cases can be found in `test__my_app.py`.
Here, the server is launched in one process and the tests are carried out
in another. The tests take advantage of `pytest.fixtures`, a `conftest.py`,
and various configuration options.

## Author

- Matt Runyon (the `tests` folder and its contents)
- Anonymous (the `app` folder and its contents)