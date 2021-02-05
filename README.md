# MIT Libraries - Dome Reports

## Synopsis

A project to query the dome.mit.edu repository for descriptive statistics and
then generate monthly content reports. 

## Setup

This project takes as a given the existing dome.mit.edu instance and the underlying Postgres database in particular.

- SQL queries to be run against the Postgres database underlying dome.mit.edu.

- SQLite3 database

  This database is a cumulative accounting of the contents of Dome taken monthly.
  The database file "drp.db" in this GitHub project has the appropriate
  tables created from the DDL script db-ddl.sql, but the tables are empty.
  The production instance of the database will be supplied with new data each month.
  A test database is available in the "tests" directory and can be specified
  in a command-line argument in the scripts.

- Python3 with libraries: sqlite, numpy and pandas [Note: we're currently testing with Python 3.7]

    for excel spreadsheet support in pandas, the following may be required:

    - pip3 install --upgrade wheel
    - pip3 install --upgrade setuptools

    for markdown support:

    - pip3 install tabulate


## Operation

The Python 3 scripts to create reports on the Dome contents are run from the command line and report files are generated.  Command line options allow for different format types.
    - monthly-collection-item-rpt.py
  

## Tests

Describe and show how to run the tests with code examples.

## Contributors

Carl Jones

## License

MIT License
