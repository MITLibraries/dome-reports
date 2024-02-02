# MIT Libraries - Dome Reports

#### Synopsis

The 'Dome Reporting Project' (DRP) is a commandline application for generating descriptive content reports for the digital collections in Dome, the **dome.mit.edu** repository, an implementation of DSpace6.x.  Usage reports are not included.  Data is obtained by querying the underlying Postgres database for Dome on a monthly basis.  The resulting field-delimited files are transferred to the local reporting workstation where the data is imported into an ongoing SQLite database which contains additional back-end management data for the Dome reports. The monthly shapshots support viewing changes over time. The content reports are then rendered in various formats (HTML, XLSX, ASCII, MARKDOWN, TXT).  DRP is a Python 3 application with development managed through GitHub.  This project is covered by the MIT license.

DRP version 0.3 is very similar to v.0.2.  It accomodates changes in the
Pandas library when writing the writing the row of monthly totals.  It provides no new features.

#### An Operations and Data Flow Diagram

[Diagram for the Dome Reports process] (docs/automation-workflow.png)

#### Setup

SQL queries are run against the Postgres database on a separate server as specified by the system administrator.  The generated csv files (.csv) are transferred to the local reporting workstation or other server.

Currently, the local reporting workstation is a Mac running OS X and requires the following software:

    - The System shell is **zsh**.
    - Python 3.11.x or higher with libraries:  sqlite, pandas, numpy
    - SQLite3 database (included in Python 3.7+, but is installed separately for optional non-Python access)

      For Excel spreadsheet support in pandas, the following may be required:

          -> pip3 install --upgrade wheel
          -> pip3 install --upgrade setuptools

Setup instructions summary for a working/production installation

  1.  Download the project from GitHub into a new directory, e.g. 'drp'
  2.  Install or confirm Python 3.11 or higher, preferred: 3.11
      Install or confirm Pandas 2.2.x or higher
  3.  Create a Python virtual environment with the libraries listed in the requirements.txt file
  4.  In the drp/db subdirectory, run the SQL initialization script 'db-ddl.sql' to create a new database with empty tables, either using a standalone SQLite at the command line as in: 
      ```
      (ve311) $> sqlite3 drp.db < db-ddl.sql
      ```
      or using the one in Python.  Change the name as needed, e.g. to 'test.db' for initial tests. 
      Or, if upgrading from the previous version, copy the old database file(s) to the new db/ directory.
  5.  For the reports to be used, edit the config.py file in the reports' subdirectories.
    Create the data subdirectories that correspond to the names in the config file.  Defaults have not been provided since Git doesn't allow empty directories.

#### Application directory structure

The directory structure for v.0.3 is the same as in v.0.2 from the previous version.  The SQLite3 database from the previous version can (or should) be copied over to the new DRP location as needed.

Downloading or cloning the GitHub project to a local directory can serve as the top level working directory for the application.  However, it is probably best to separate any application development from performing production reporting. Note that the directory setup has not changed in v.0.3.

It is recommended to use a Python virtual environment.  The virtual environment can exist inside or outside the project directory.  However, once created it should not be moved to another location on the filesystem. The list of required libraries "requirements.txt" is included in the top level DRP directory.

The top level directory:
```
        drp_3.x                  # the name can vary
        ├──db/                   # SQLite3 database(s)
        ├──docs/
        ├──postgres/             # shell scripts for querying the Postgres database
        ├──r_cicah/              # report "Collection Item Counts - Ad Hoc"
        ├──r_cicmts/             # report "Collection Item Counts, Monthly Time Series"
        ├──r_***/                # any new reports
        ├──shared/               # common python code and configuration shared across reports
        ├──
        └── tmp/                  # as needed
        venv3.11
```

The local SQLite database is central and shared across the various reports.
The configuration structure is specified as a Python dataclass in the shared/config.py file. Each reports implements this dataclass with values appropriate to its needs. 

Each report is run as a separate Python 3 (.py) file in its dedicated "r_" subdirectory. The naming convention for reports is to start with "r_" but this is not required.

The report subdirectory structure:
```
        r_{name}                # the name
        ├──data_in/             # input data files, i.e. .csv from Postgres
        ├──data_done/           # processed data files moved here after ingest
        ├──rpts_out/            # generated reports
        ├──config.py            # local configuration file
        ├──{name}.log           # Python logging file
        └──*.py                 # Additional code libraries as needed
```

#### Configuration

Configuration is handled using a custom Python dataclass with a structure is centrally defined in the top level config.py but leaving the configuration values to be defined for each report separately.

#### Logging

Logging is configured centrally in the top level config.py, but is done in a way such that each report has its own log file in that report's directory.

Python standard logging is used in the Python scripts. Log entries are written by default to both the console and the file "logs/drp.log" to store events and errors with timestamps in order to assist with tracking problems.  There is an alternate logging configuration file to specify writing only to the file and not to the console.

The log levels of both the console log and the file log are adjustable in configuration.  The default is "info".  There are plenty of "debug" log entries, should the level be changed to that.

#### Postgres queries

The model shell script for querying the Dome Postgres database is in the postgres subdirectory: postgres/drp_pg.sh.

The data files can be used for different DRP reports.

For the current three Postgres queries, the resulting delimited csv data files have file names formatted as:  {name}-{YYMM}.csv, e.g. comm-2102.csv, coll-2102.csv, itct-2102.csv for community, collection and item-counts for February 2021.  The year and month in the file names are essential for processing the data for report generation and identifying which files are for which month.  The rows in the item-count files also have the year and month listed as fields.


#### Running reports

It is recommended to use a Python virtual environment with the appropriate libraries installed there.

At the commandline, a report can be run from any directly that specifies the correct path to the report Python .py file.  It would be typical to run a report from the main project directory, e.g. as:

(ve311) $> python3.11 ./r_cicmts/cicmts.py

Commandline arguments can vary by report.  Most of these override a configuration option, so typically will
not be needed for routine reporting.  An example where this might be useful would be where an additional
report file needs to be generated in a different format from that specified in configuration.


#### The DRP database

The DRP database is an SQLite3 database shared across the various DRP reports.  The database file, named **drp.db** by default, is located in the "db/" subdirectory.  Additional database files can be used and specified in configuration or on the commandline, e.g. "test.db".

The DRP database maintains tables with partial or summary data from the Dome implementation of DSpace.  In the case of the Community and Collection tables, the data consists of name and uuid data from Dome as well as fields that are used for local management purposes.  The Item_Count table keeps stateful data on a monthly basis to support time-series reporting.  Other tables in the DRP database contain DRP management data.

For test purposes, it may be useful to have a second database file and use the report configuration or a commandline argument to temporarily use this alternate db.  Care should be taken in doing this and it may be preferable to use an entirely separate DRP installation for testing.

In addition to the summary data in the local db, there are some additional columns and tables that provide additional data to support the management of the reports and potentially the management of Dome.

The SQLite database for this project is intended to supply reports over time and, consequently, represent the data over the future lifespan of Dome.  In the event that, for example, a collections is deleted from Dome, the corresponding data should not be deleted from the SQLite database in order that time-series reports can accurately represent the relevant time-span.  For the Dome communities and collections, the SQLite database does not represent any current state of Dome.  For things like item counts, snapshots over time are recorded and the relevant year and month are recorded for each count.

There are several ways to view the SQLite3 database directly:

*  The SQLite3 commandline
*  A GUI application such as DB Browser

The latter is particularly useful in editing management data.

The fields for the SQLite tables are:

#### Community
```
        ├─ uuid
        ├─ name                     # as used in Postgres
        ├─ short_name               # version of name used in reports, the same as 'name' by default
        └─ notes
```
Only one, i.e. the lowest, level of the Dome community structure is used by DRP.

#### Collection
```
        ├─ uuid
        ├─ comm_uuid                # reference to a containing community
        ├─ name                     # as used in Postgres
        ├─ short_name               # version of name used in reports, the same as 'name' by default
        ├─ reportable               # whether to include in reports, default is True
        ├─ owner                    # institutional unit responsible for the collection
        └─ notes

```
By default, the name and short_name values are the same. Short_names allow for better report presentation, since the Dome community and collection names can be very long.  However, it requires manual editing to alter the short_name fields.


#### Monthly_Item_Count
```
        ├─ coll_uuid                # id of containing collection
        ├─ year                     # integer: YYYY
        ├─ month                    # integer: 1 through 12, the current month when the report runs
        └─ item_count               # integer: default is 0
```

#### Files_Processed
```
        ├─ name                    # file name
        └─ timestamp               #
```
To ensure that data files are not processed repeatedly, this table is used to record file names.
In the event of an ingest error, this table can be edited to allow for a repeat. 

#### Email_Distribution
```
        ├─ name
        ├─ email
        ├─ formats                 # array of format codes
        ├─ active                  # on/off
        └─ note
```
SQLite3 does not support an ENUM datatype, but formats can suffice for now as a string of single-letter codes to designate the formats:
a - ASCII text; c - CSV; h - HTML; m - Markdown; x - XlSX (Excel).  For example:  'hx'.

## Tests
The tests/ subdirectory contains test data.

The script test_data.sql is to be run directly by SQLite3 and loads initial community and collection entities as well as item counts for Jan to Apr of 2021.

The .csv files are test data files used for simulating monthly loads and cover May to Dec of 2021.  Note that the Dec files introduce a new collection.  To run reports on this data, it is necessary to change the year to 2021 in the report's config.py file. 

## Reports

###Report #1: CICTMS - Collection Item Count Monthly Time Series

This report lists the monthly totals in a given year for all the Dome collections organized by their containing communities.  Since Dome makes minimal use of the hierarchical community structure, only one level of communities is used in the reports which is adequate to clearly identify and contextualize the collections.  Empty collections are included.

In order to automate the update the Community and Collection tables with data from Postgres without clobbering the existing data,
**only new** Collections and Communities are imported into the SQLite database.  The Python import script filters out the pre-existing data rows from the import file.  Manually updating these extra fields can be done using an applications such as DB Browser for SQLite.

The item counts only include owned items, and not items linked to other collections.  Items in process (workflow) or that have been deleted are also not included.  In the Monthly_Item_Count table, there is a uniqueness constraint for the collection, year and month, so that multiples will be rejected.

This report is a monthly time series for the span of one calendar year.  For the month of January there is only one column; for December there are twelve.  Combining multiple reports after the fact should provide adequate access to different report intervals.  In the event of missing  a month's input, subsequent reports will run properly, but the reports will omit the missed month's column of data.

In the event of an invalid data load, all of that data will need to be deleted manually from the database
prior to loading the correct data.

#### A sequence of operations.

The CICMTS report runs in the following sequence:

1. Run the Postgres queries and move the resulting 3 .csv data files into the report's "data-in" subdirectory.

2. Run cicmts.py to read in the 3 Postgres .csv data files and load them into the local database on a monthly basis to support the timeseries.  The latter part of cicmts.py queries the local database for all the months in the current or some previous year.  Python's "Pandas" library is used to reshape the data and write out the reports. Either of the two parts can be run alone, as needed.

3. Report distribution is not currently included in the automation.

#### Postgres queries

  The model shell script for querying Postgres is in the postgres subdirectory: drp_pg.sh .  This consists of three queries resulting in three files.

  The resulting delimited csv data files are produced for the Dome Communities, Collections and the specific for the available reports.
  The filenames are formatted as:  {name}-{YYMM}.csv, e.g. comm-2102.csv, coll-2102.csv, itc-2102.csv for community, collection and item-counts for February 2021.
  The year and month in the file names are essential for processing the data for report generation and identifying which files are for which month.  The rows in the item-count files also have the year and month listed as fields.

#### Running the CICTMS report

After running the Postgres queries for the current month,

At the commandline, a report can be run from any directly that specifies the correct path to the report Python .py file.  It would be typical to run a report from the main project directory, e.g. as:

(venv311) $> python3.11 ./r_cicmts/cicmts.py

Most of these override a configuration option, so typically will
not be needed for routine reporting.  An example where this might be useful would be where an additional
report file needs to be generated in a different format from that specified in configuration.  In this case, one can suppress the data file ingest and specify the output format with the arguments "-k -fa".

The commandline help text can be displayed with the argument "-h"

Available option parameters: (None of these is required)
```
       -h --help                help
       -k --skip_ingest         only write reports based on database contents
       -p --skip_rpts           only ingest new data files
       -i --data_dir_path
       -o --rpts_dir_path
       -f --fmts                accepts multiples, see note below for codes
       -d --db                  use other database file
```

where the formats for option 'f' are:
```
      - a = ascii (default)
      - c = csv
      - h = html
      - m = markdown
      - x = xlsx (excel)
      - s = screen console display (default if not others are listed)
```

  example:
```
   (ve311> $>python311 r_cicmts/cicmts.py -fas -d/path/to/test.db -o./tests
```

The cicmts.py report script is for reporting once a month.  It will return an error if item count data for a given month is repeated.  In case of correcting errors, the old data will need to be removed manually.  And for reusing the data files from Postgres, the FilesProcessed table will need to be manually edited.  It is possible to skip months which will result in fewer columns in the output reports.


### Report #2: CICAH - Collection Item Count - "Ad Hoc"

This "ad hoc" report is for reporting the Collection Item Count status at a given moment in time. For input data, it uses the same itct-????.csv files that the time-series report uses. Unlike the time-series report, running this report does not store the item count data in the DRP db.

After running the Postgres queries for the current month,

At the commandline, a report can be run from any directly that specifies the correct path to the report Python .py file.  It would be typical to run a report from the main project directory, e.g. as:

(venv311) $> python3.11 ./r_cicah/cicah.py

Commandline usage:
```
     (ve311) $>python311 /path/to/rpt_cicah.py
```
Available option parameters: (None of these is required)
```
        -h <--help>
        -i <--data_dir_path= ...>
        -o <--rpts_dir_path= ...>
        -f <--rpt_fmts= same as CICMTS
        -d <--db_file_path= ...>
```

##=================

#### Contributors

W. Hays
Carl Jones

#### License

MIT License
