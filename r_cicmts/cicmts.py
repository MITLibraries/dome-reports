# CICMTS - Collection Item Counts Monthly Time Series Report
# The span of the time series is one year, Jan to Dec.
# The span may be extended in future versions.

# append 'shared' module in the root directory to sys.path
from sys import path as syspath
from pathlib import Path
rootpath = Path(__file__).parents[1]
syspath.append(str(rootpath))
import shared.drplib as drp
import shared.config

from sys import argv, exit
from contextlib import closing
from getopt import GetoptError
from datetime import datetime

import logging
import csv
import calendar
import sqlite3
import pandas as pd

import config    #local

# instantiates the config and updates per the commandline options
# calls run(), the top level processing function
def main(argv):

    cfg = config.get_config()

    # init logging
    shared.config.log_init(cfg.rpt_dirpath / "cicmts.log",
                 cfg.log_file_level,
                 cfg.log_console_level,
                 cfg.log_file_append)

    logging.info(f"DRP module CICMTS, version {cfg.version}")

    #commandline options, with potential to override config values
    try:
        config.get_commandline_options(argv, cfg)
        config.validate_config(cfg)
    except GetoptError as e:
        logging.error(e.msg)
        print(config.get_help_text())
        drp.cleanup_and_exit(1)
    except AssertionError as msg:
        logging.error(msg)
        #print(config.get_help_text())
        drp.cleanup_and_exit(1)
    except ValueError as msg:
        logging.error(msg)
        print(config.get_help_text())
        drp.cleanup_and_exit(1)

    run(cfg)

def run(cfg):

    logging.info(f"Using database file {cfg.db_filepath}")

    # ingest and reporting
    try:
        with closing(sqlite3.connect(cfg.db_filepath)) as conn:
            conn.execute("PRAGMA foreign_keys = 1")
            with closing(conn.cursor()) as cursor:
                if cfg.skip_ingest:
                    logging.info("Skipping data ingest")
                else:
                    run_ingest(conn, cursor, 
                        cfg.data_in_filename_filters, cfg.data_in_field_sep,
                        cfg.data_in_dirpath, cfg.data_done_dirpath)

                if cfg.skip_output:
                    logging.info("Skipping report generation")
                else:
                    itct_rows = query_rpt_data(conn, cursor,
                                            cfg.rpt_year)
    except AssertionError as msg:
        logging.error(f"Error validating data ingest files: {msg} ")
        drp.cleanup_and_exit(1)
    except sqlite3.Warning as w:
        logging.warning(f"Ingest warning: {w}")
        drp.cleanup_and_exit(1)
    except sqlite3.Error as e:
        logging.error(f"Ingest error: {e}")
        drp.cleanup_and_exit(1)

    if not cfg.skip_output:
        try:
            generate_report_files(itct_rows,
                    cfg.rpts_out_dirpath, cfg.rpt_basename,
                    cfg.rpt_formats, cfg.rpt_year)

        except AssertionError as msg:
            logging.error(msg)
            drp.cleanup_and_exit(1)

    # if not cfg.skip_distr:
        # try:
            # email rpts

    logging.info("End of DRP CICMTS run")
    drp.cleanup_and_exit(0)

# ingest any combination of comm, coll, or itct files
# can raise AssertionError or ValueError
def run_ingest(conn, cursor, f_filters, field_sep, data_in_dirpath, done_dirpath):

    logging.info("starting data ingest")
    logging.info(f"ingest file dir: {data_in_dirpath}")

    # validate and return the comm, coll, and itct filepaths in that order
    #infiles = get_ingest_filepaths(cfg.ingest_dicfgth, file_filters)
    comm_file, coll_file, itct_file  = \
                  get_ingest_filepaths(data_in_dirpath, f_filters)

    # load data from files into db
    if comm_file is not None:
        ingest_dome_containers(conn, cursor, "Community", comm_file,
                           field_sep, done_dirpath)

    if coll_file is not None:
        ingest_dome_containers(conn, cursor, "Collection", coll_file,
                           field_sep, done_dirpath)

    if itct_file is not None:
         ingest_item_counts(conn, cursor, itct_file, field_sep, done_dirpath)

    logging.info("Ingest complete")


# sort the filepaths for files in the ingest directory 
# according to the source types:  community, collection, item counts
# indicated in their names as shown in the filename filters
# since the ingest directory has similarly named files moving in
# and out over time, it is prudent to verify that the current
# file contents are consistent in number and date for the expected run
# so various assertions are applied herein
def get_ingest_filepaths(dirpath, filters):
    # use the filters to group the filenames per type (comm, coll, itct)
    # this will result in a list of 3 lists ordered as the filters
    fsorted = [list(dirpath.glob(ffilter)) for ffilter in filters]
    logging.debug(f"fsorted: {fsorted}")

    # check for 0 or 1 file per source type, e.g.. 1 comm, 1 coll, 0 itct
    assert (all([(len(x)<2) for x in fsorted])), \
           "should be one or no filepath for each source type (comm, coll, itct)"

    # reduce to simple list of three filenames or None for missing file
    flattened = [None if len(x) == 0 else x[0] for x in fsorted]
    logging.debug(f"flattened: {flattened}")

    assert (not all([x is None for x in flattened])), \
           f"No files to process in {dirpath.name}"

    # verify the last part of the name with the year and month is the same
    # for each file
    fn_tails = [x.name[-9:] for x in flattened if x is not None]
    assert (len(set(fn_tails)) == 1), \
           "ingest filenames do not match in the year/month in their names"

    return tuple(flattened)

# insert data into the community or collection tables
def ingest_dome_containers(conn, cursor, tablename, filepath,
                           sep, done_dirpath):
    logging.info(f"ingesting file: {filepath.name}")
    assert not drp.datafile_processed(cursor, filepath), \
          f"{filepath.name} already processed. Please move file to continue."

    with open (filepath, 'r') as f:
        irows = [irow for irow in csv.reader(f, delimiter=sep)]
        logging.debug(f"count of rows in {filepath.name}: " + str(len(irows))) 

    assert (irows is not None), f"Error reading {filepath.name}"
    assert (len(irows) > 0), f"{filepath.name} is empty"

    # a soft transition to adding the handle as the last field in the csv file
    # check first row for the number of fields
    nfields = len(irows[0])

    if tablename == "Community":
        if nfields == 3:
            insert_query = \
            "INSERT INTO Community(uuid, name, short_name) VALUES (?, ?, ?)"
        elif nfields == 4:
            insert_query = "INSERT INTO Community" + \
            "(uuid, name, short_name, handle) VALUES (?, ?, ?, ?)"
        else:
            ms = f"Incorrect number of fields, {nfields}, in input file {filepath.name}"
            raise ValueError(ms)
    else:  #Collection
        if nfields == 4:
            insert_query = "INSERT INTO Collection" + \
            "(uuid, comm_uuid, name, short_name) VALUES (?, ?, ?, ?)"
        elif nfields == 5:
            insert_query = "INSERT INTO Collection" + \
            "(uuid, comm_uuid, name, short_name, handle) VALUES (?, ?, ?, ?, ?)"
        else:
            ms = f"Incorrect number of fields, {nfields}, in input file {filepath.name}"
            raise ValueError(ms)

    #get all container uuids from db
    db_rows = cursor.execute("SELECT uuid FROM " + tablename).fetchall()
    logging.debug(f"{tablename} row count: {str(len(db_rows))}")

    nadded = 0;
    if len(db_rows) == 0:
        logging.info(f"db table {tablename} is empty; loading all rows in file")
        cursor.executemany(insert_query, irows)
        nadded = len(irows)
    else:
        # filtering file  for new rows in db 
        db_uuids = set()

        for db_row in db_rows:
            db_uuids.add(db_row[0])

        logging.debug("uuid set size: " + str(len(db_uuids)))

        nadded = 0
        for irow in irows:
            if irow[0] not in db_uuids:
                cursor.execute(insert_query, irow)
                nadded += 1

    logging.info(f"Count of added rows to {tablename}: {nadded}")

    cursor.execute("INSERT INTO FilesProcessed(name, timestamp) VALUES " + \
        "(?, CURRENT_TIMESTAMP);", (filepath.name, ))
    logging.debug("recorded processed data file")
    conn.commit()
    logging.debug("committed data from " + filepath.name)
    logging.info(f"Processed {filepath.name} with {nadded} new rows added")

    filepath.rename(done_dirpath / filepath.name)
    logging.info(f"moved {filepath.name} to completed directory")


def ingest_item_counts(conn, cursor, filepath, separator, data_done_dirpath):

    logging.info(f"ingesting file: {filepath.name}")
    assert not drp.datafile_processed(cursor, filepath), \
           "{filepath.name} already processed. Please move file to continue."

    with open (filepath, 'r') as f:
        irows = [irow for irow in csv.reader(f, delimiter=separator)]
        logging.debug(f"count of rows in {filepath.name}: " + str(len(irows))) 

    assert (irows is not None), f"Error reading {filepath.name}"

    assert (len(irows) > 0), "File {filepath.name} is empty"

    insert_query = "INSERT INTO Monthly_Item_Count" + \
        "(coll_uuid, year, month, item_count) VALUES (?, ?, ?, ?);"
    cursor.executemany(insert_query, irows)
    logging.debug(f"Inserted {len(irows)} item_counts") 

    cursor.execute("INSERT INTO FilesProcessed(name, timestamp) VALUES " + \
        "(?, CURRENT_TIMESTAMP);", (filepath.name, ))
    logging.debug(f"recorded processed file {filepath.name}")
    conn.commit()
    logging.debug(f"committed data from {filepath.name}")
    #logging.info(f"Processed {filepath.name}")

    filepath.rename(data_done_dirpath / filepath.name)
    logging.info(f"moved {filepath.name} to completed directory")


# Get current data from the DRP local db for creating the CICMTS report
# Returns list of column rows and list of monthly item counts rows
def query_rpt_data(conn, cursor, year):
    logging.info("Starting report generation")

    queryItcts = ("SELECT comm.short_name as Community, "
          "coll.short_name as Collection, month, item_count "
          "FROM Community comm "
          "JOIN Collection coll ON comm.uuid = coll.comm_uuid "
          "LEFT JOIN Monthly_Item_Count itc ON coll.uuid = itc.coll_uuid "
          "WHERE (year = ? OR year IS NULL) AND coll.reportable = 1 "
          "ORDER BY coll.comm_uuid, coll.name;")

    itct_rows = cursor.execute(queryItcts, (year,)).fetchall()

    #validate results
    logging.debug(f'Count of item count rows: {len(itct_rows)}')
    assert len(itct_rows) > 0, f"No data in for year {year}"

    return itct_rows


# Generate a pivot table from the item data such that
# the rows are for each Collection and the columns are for each month
# In order to ensure that  empty collections are included
# a left join is used in the query below
def get_data_frame(itct_rows):

    df_itct = pd.DataFrame(itct_rows)
    df_itct.columns = ["Community", "Collection", "Month", "Count"]

    #For any rows with null month and count
    #set month to the most frequent month "mode"
    #set count to 0
    month_mode = df_itct['Month'].mode().iat[0]
    df_itct['Month'] = df_itct['Month'].fillna(month_mode)
    df_itct['Count'] = df_itct['Count'].fillna(0)

    ptable = df_itct.pivot_table( index=["Community", "Collection"],
              values=["Count"], columns=["Month"], fill_value=0, aggfunc=max)

    #extract column integers (will these always be sorted?)
    #i.e. the exact months in query result, skipping months with no data
    ar_mo_int = [ int(j) for i, j in ptable.columns.to_flat_index().to_list()]
    #get array of corresponding months
    ptable.columns = [calendar.month_abbr[i] for i in ar_mo_int]

    #Monthly totals across all collections
    sums = ptable.sum(numeric_only=True)
    ptable.loc['Totals'] = pd.Series(sums)

    logging.debug(f"Dimensions of pivot table: {ptable.shape}")

    return ptable


# the filename stem indicates the period reported on
# param 'year' is for the period reported on
def generate_report_files(itct_rows, rpts_dirpath,
                          rpt_basename, rpt_fmts, year ):

    df = get_data_frame(itct_rows)

    now = datetime.now()

    if year == now.year:
        stem = f"{rpt_basename}-{now.year}{now.month:02}"
    else:
        stem = f"{rpt_basename}-{year}"

    drp.write_rpts(df, rpt_fmts, rpts_dirpath, stem, year)


if __name__ == "__main__":
    main((argv[1:]))
