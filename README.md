# MIT Libraries - Dome Reports

## Synopsis

A project to generate monthly content reports for the dome.mit.edu repository.

## Setup

This project takes as a given the existing dome.mit.edu instance and the underlying Postgres database in particular.

- SQLite3 database

  <description>

- Python3 with libraries: sqlite, numpy and pandas

    for excel spreadsheet support in pandas, the following may be required:

    - pip3 install --upgrade wheel
    - pip3 install --upgrade setuptools

    for markdown support:

    - pip3 install tabulate


## Operation

The Python3 script is run from the command line and report files are generated.

## Tests

Describe and show how to run the tests with code examples.

## Contributors

Carl Jones

## License

MIT License
