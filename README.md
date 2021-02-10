# MIT Libraries - Dome Reports

## Synopsis

A project to generate reports from the Postgres database underlying Dome, the **dome.mit.edu** repository.  After querying Postgres for descriptive statistics, the resulting files are transferred to the local reporting workstation and stored in an ongoing SQLite database.  Content reports are then generated using Python 3 scripts from the command line.

## Setup

- SQL queries are run against the Postgres database on a separate server in a separate process from the report generation as specified by the system administrator.
  The generated tab-delimited data files (.tsv) are transferred to the local workstation for processing.
  [TODO: query details]

- The local workstation requires preloading the following software:

    - Python 3.7.x or higher with libraries:  sqlite, pandas, numpy (tabulate for markdown support)
    - SQLite3 database (included in Python 3.7+, but is installed separately for optional non-Python access)

      For excel spreadsheet support in pandas, the following may be required:
      
          -> pip3 install --upgrade wheel
          -> pip3 install --upgrade setuptools

- The directory/file structure in production:

```
        dome-reports/
        ├── db/                 #  sqlite database scripts
        ├── docs/               # 
        ├── imports/            #  for Postgres query result data files (.tsv)
        │   └── done/           #  for import files after successful reporting
        ├── rpts/               #  generated reports
        ├── tests/              #  for an SQLite database with test data
        │
        ├── drp-db              #  the SQLite3 database (do not delete! keep a backup!)
        ├── import.py           #  Python script with options for all imports of Postgres query data
        ├── <...rpt...>.py      #  various Python scripts for the different reports
        │
        ├── README.md
        └── LICENSE

```

## Postgres queries

  [TODO:  querying details]

  The resulting tab-delimited data files are produced for the Dome Communities, Collections and the specific for the available reports.
  The filenames are formatted as:  {name}-{YYMM}.tsv, e.g. comm-2102.tsv, coll-2102.tsv, itc-2102.tsv for community, collection and item-counts for February 2021.
  The year and month in the file names are essential for processing the data for report generation and identifying
  which files are for which month.  The rows in the item-count files also have the year and month listed as fields. 

## SQLite database imports

The SQLite database "drp.db" contains tables for the Dome Community and Collection entities which are the standard DSpace containers for repository items.  For reporting purposes it is useful to maintain additional data for these entities.  Here are the fields for parallel SQLite  tables:

#### Community 
```    
        ├─ uuid                     
        ├─ name                     # as used in Postgres
        ├─ short_name               # version of name used in reports, the same as 'name' by default
        └─ notes                    
```

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

Only one level of community is supported here; i.e. there is no subcommunity nesting.
Short_names allow for better report presentation, since the Dome community and collection names can be very long.

In order to automate the update these two tables with data from Postgres without clobbering the added data,
**only new** Collections and Communities are imported into the SQLite database.  The Python import script filters
out the pre-existing data rows from the import file.

Manually updating these extra fields can be done using an applications such as DB Browser for SQLite.


#### Report: Collection_Item_Counts.py
```
        ├─ coll_uuid                # id of containing collection
        ├─ year                     # integer: YYYY
        ├─ month                    # integer: 1 through 12, the current month when the report runs
        └─ item_count               # integer: default is 0
```

This report is intended to be run once a month resulting in a time series for the current calendar year.
There is a uniqueness constraint for the collection, year and month, so that multiples will be rejected.
In the event of an invalid data load, all of that data will need to be deleted manually from the database
prior to loading the correct data.

## Longer term processing issues

Various problems can arise with sequential processing across difference servers and applications over many months and years.  The following outlines how some of this is handled, especially in the automated aspects.

**Duplicate processing of import files**  The SQLite database maintains a table listing all processed filenames.  This will be checked before attempting an import on a file.  In addition, processed files in the /imports directory will be automatically moved to the /import/completed directory.  To be determined: deleting or moving completed files at some point.

**Missing import files or lapses in process**  External factors may interfere with monthly processing or access to the source database and repository.  The report generation scripts will adapt to the possibility of missing data with codes such as N/A (not available) and so forth.  Attempting to capture data from previous months based on accession timestamps is not currently envisioned.

**Log of events and errors**  There is a table named "Log" in the database which will store events and errors with timestamps in order to assist with tracking problems.

**Time-series intervals**  Currently, the monthly reports are set to appear per calendar year in single reports.  Combining multiple reports after the fact should provide adequate access to different report intervals.

## Ad hoc reports

An attempt will be made to reuse existing functionality.  For one-time queries to get at the current state,
the SQLite database will probably not be needed.  There is a variety of software tools that can format and
output reports.


## Report generation 

The Python 3 scripts to create reports on the Dome contents are run from the command line and report output files are generated.  Currently available reports:

### collection-item-counts.py

This report is a yearly time-series accounting of the item contents of each collection in Dome in monthly increments.

Command line options allow for different format types, e.g. HTML, ASCII, Excel and Markdown. 


## Report Distribution

[TODO]
It would be handy and efficient if the Dome Reports could be posted in a Community/Collection in Dome itself.


## Tests

A test database is available in the "tests" directory and can be specified in a command-line argument for some report scripts.

[TODO: Describe and show how to run the tests with command line examples.]

## Contributors

Carl Jones

## License

MIT License
