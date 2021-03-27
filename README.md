# MIT Libraries - Dome Reports

## Synopsis

A project to generate descriptive reports for the digital collection in Dome, the **dome.mit.edu** repository.  Usage reports are not included.  Data is obtained by querying the underlying Postgres database for Dome.  The resulting field-delimited files are transferred to the local reporting workstation where the data is imported into an ongoing SQLite database.  Content reports in a variety of formats are then generated and distributed.

#### An Operations and Data Flow Diagram

[Diagram for the Dome Reports process] (docs/automation-workflow.png)

## Setup

- SQL queries are run against the Postgres database on a separate server as specified by the system administrator.  The generated tab-delimited data files (.tsv) are transferred to the local reporting workstation.

- The local reporting workstation is a Mac running OS X and requires the following software:

    - The System shell is **zsh**.
    - Python 3.7.x or higher with libraries:  sqlite, pandas, numpy (tabulate for markdown support)
    - SQLite3 database (included in Python 3.7+, but is installed separately for optional non-Python access)

      For excel spreadsheet support in pandas, the following may be required:

          -> pip3 install --upgrade wheel
          -> pip3 install --upgrade setuptools

#### Recommended overall directory structure

The following directory setup is aimed at providing maximum separation between a git development environment,
a production environment and a test environment.  Python virtual environments are optional, but further separating the Python virtual environments allows easily switching between, say, different versions of Python.

        drp_root                # name can vary
        ├──git_repo             # clone or unzip the github repository here, the subdirectory name can vary
        ├──prod                 # production area; created by the deploy_prod.sh script
        ├──test                 # test area; created by the deploy_test.sh script
        ├──venv3.7              # optional python virtual environment 
        ├──venv3.8              # as needed
        ├──tmp                  # as needed
 

#### Deploy scripts

The deploy scripts **deploy_prod.sh** and **deploy_test.sh** are used to create the separate production and test environments and populated them with the required subdirectories and files.  There are no interdependencies between **prod** and  **test**.

Both scripts do the following: 

    - subdirectories are created
    - scripts are copied
    - an SQLite3 database is created with the necessary tables; the databases names are distinct.

Care should be used to avoid moving data into the wrong database.

- The directory/file structure in both **prod** and **test**:

```
        ├── docs/                      # 
        ├── imports/                   #  for Postgres query result data files (.tsv)
        ├── imports_completed          #  for import files after successful reporting
        ├── logs
        ├── postgres                   #  scripts for retrieving import data
        ├── reports/                   #  generated reports
        │
        ├── drp<...>-db                #  the SQLite3 database (do not delete! keep a backup!)
        ├── import_data.py             #  Python script with options for all imports of Postgres query data
        ├── collection_item_counts.py  #  Python script to generate time-series reports of item counts for all collections 
        └── <...>.py                   #  other Python scripts for the different reports

```

## Postgres queries

  The model shell script for querying Postgres is: drp_pg.sh .  

  The resulting tab-delimited data files are produced for the Dome Communities, Collections and the specific for the available reports.
  The filenames are formatted as:  {name}-{YYMM}.tsv, e.g. comm-2102.tsv, coll-2102.tsv, itc-2102.tsv for community, collection and item-counts for February 2021.
  The year and month in the file names are essential for processing the data for report generation and identifying
  which files are for which month.  The rows in the item-count files also have the year and month listed as fields. 

## SQLite database imports

The SQLite production database "drp_prod.db" contains tables for the Dome Community and Collection entities which are the standard DSpace containers for repository items.  For reporting purposes it is useful to maintain additional data for these entities.  The fields for these SQLite tables are:

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

#### Handling of the SQLite database over time - differences with the Dome database

The SQLite database for this project is intended to supply reports over time and, consequently, represent the data
over the future lifespan of Dome.  In the event that, for example, a collections is deleted from Dome, the corresponding data
should not be deleted from the SQLite database in order that time-series reports can accurately represent the relevant
time-span.  For the Dome communities and collections, the SQLite database does not represent any current state of Dome.
For things like item counts, snapshots over time are recorded and the relevant year and month are recorded for each count.

#### Monthly data imports: import_data.py

The monthly import script is for reporting once a month.  It will return an error if item count data for a given month is repeated.  In case of correcting errors, the old data will need to be removed manually.  It is possible to skip months which will result in fewer columns in the output reports.
 
Command line usage: 
```
  python3 import_data.py -h(elp) -i <import_dir> -c <complete_dir> -d <database>
  
  The default SQLite3 database file is drp_prod.db.
  The default import directory is ./imports.
  The default completed directory is ./imports-completed
  
```

#### Report: collection_item_counts.py
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

## Logging

Python standard logging is used in the Python scripts. Log entries are written by default to both the console and the file "logs/drp.log" to store events and errors with timestamps in order to assist with tracking problems.  There is an alternate logging configuration file to specify writing only to the file and not to the console.

## Longer term processing issues

Various problems can arise with sequential processing across difference servers and applications over many months and years.  The following outlines how some of this is handled, especially in the automated aspects.

**Duplicate processing of import files**  The SQLite database maintains a table named "Files_Processed" that lists all processed filenames.  This will be checked before attempting an import on a file.  In addition, processed files in the /imports directory will be automatically moved to the /imports_completed directory.  To be determined: deleting or moving completed files at some point.

**Missing import files or lapses in process**  External factors may interfere with monthly processing or access to the source database and repository.  The report generation scripts may adapt to the possibility of missing data with codes such as N/A (not available) and so forth.
In the event of reports not run in a given month, the corresponding month column may not appear, instead.  Attempting to capture data from previous months based on accession timestamps is not currently envisioned.

**Time-series intervals**  Currently, the monthly reports are set to appear per calendar year in single reports.  Combining multiple reports after the fact should provide adequate access to different report intervals.

## Ad hoc reports

An attempt will be made to reuse existing functionality.  For one-time queries to get at the current state,
the SQLite database will probably not be needed.  There is a variety of software tools that can format and
output reports.


## Report generation 

The Python 3 scripts to create reports on the Dome contents are run from the command line and report output files are generated.  Currently available reports:

### collection-item-counts.py

This report is a yearly time-series accounting of the 'owned' item contents of each collection in Dome in monthly increments in different and multiple format types, e.g. HTML, ASCII, Excel and Markdown. The default year is the current year. 

Command line usage: 
```
  python3 collection-item-counts.py -h(elp) -y <year> -f <formats> -d <database> -o <output dir> -s <console output>
  
  where the formats can be: 
      - a = ascii (default) 
      - c = csv 
      - h = html 
      - m = markdown 
      - x = xlsx (excel)
      - s = screen console display (default is False)
      
  example:  python3 collection-item-counts.py -fhx -d./tests/test.db -o./tests     
```


## Report Distribution

Initially, reports can be emailed to specified, responsible parties.
It would be handy and efficient if the Dome Reports could be posted in a Community/Collection in Dome itself.

## Process Automation

A major goal with the project is to automate each monthly production run. 
Logging and notification of the production run status will be featured. 
[TODO: Describe the "master.zsh" shell script]

## Testing

Sample test data is provided in the GitHub repository.

Tests should be run in the test directory as created by the deploy_test.sh script.


## Contributors

Carl Jones

## License

MIT License
