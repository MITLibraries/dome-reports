# CICAH - Collection Item Counts Ad Hoc Report
# The item count status at one moment in time

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
import sqlite3
import pandas as pd

import config    #local


# the main function below instantiates the config
cfg = None

def main(argv):

    global cfg
    cfg = config.get_config()

    # init logging
    shared.config.log_init(cfg.rpt_dirpath / "cicah.log",
                 cfg.log_file_level,
                 cfg.log_console_level,
                 cfg.log_file_append)

    logging.info(f"DRP module CICAH, version {cfg.version}")

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
        drp.cleanup_and_exit(1)
    except ValueError as msg:
        logging.error(msg)
        print(config.get_help_text())
        drp.cleanup_and_exit(1)

    logging.info(f"Using database file {cfg.db_filepath}")

    try:
        coll_rows = get_coll_data()
        itct_filepath = get_itct_filepath()
        generate_reports(coll_rows, itct_filepath)

        #move processed file
        itct_filepath.rename(cfg.data_done_dirpath / itct_filepath.name)
        logging.info(f"moved {itct_filepath.name} to completed directory") 
    except AssertionError as msg:
        logging.error(msg)
        drp.cleanup_and_exit(1)
    except ValueError as e:
        logging.error(e)
        drp.cleanup_and_exit(1)

    # if not cfg.skip_distr:
        # try:
            # email rpts

    logging.info("End of DRP CICAH run")

    drp.cleanup_and_exit(0)


# Get current data from the DRP local db for creating the CICMTS report
# Returns list of column rows and list of monthly item counts rows
def get_coll_data():

    queryColls = ("SELECT coll.uuid as coll_uuid, "
          "comm.short_name  as Community, "
          "coll.short_name as Collection "
          "FROM Community comm "
          "JOIN Collection coll ON comm.uuid = coll.comm_uuid "
          "WHERE coll.reportable = 1;")

    try:
        with closing(sqlite3.connect(cfg.db_filepath)) as conn:
            conn.execute("PRAGMA foreign_keys = 1")
            with closing(conn.cursor()) as cursor:
                coll_rows = cursor.execute(queryColls,).fetchall()
    except sqlite3.Warning as w:
        logging.warning(f"Ingest warning: {w}")
        drp.cleanup_and_exit(1)
    except sqlite3.Error as e:
        logging.error(f"Ingest error: {e}")
        drp.cleanup_and_exit(1)

    #validate results
    logging.debug(f'Count of all collection rows: {len(coll_rows)}')
    assert len(coll_rows) > 0, f"Number of total collections: {len(coll_rows)}" 

    return coll_rows


def get_itct_filepath():

    logging.debug(f"input file filter: {cfg.data_in_filename_filters[0]}")
    fs = list(cfg.data_in_dirpath.glob(cfg.data_in_filename_filters[0]))
    logging.debug(f"input files found: {fs}")

    if fs is None or len(fs) == 0:
        raise ValueError("No input file found matching filter in config.")

    if len(fs) > 1:
        raise ValueError("Multiple files found matching filter in config.")

    logging.info(f"Processing input file: {fs[0].name}")

    return fs[0]


# Community and Collection data are assumed to be up-to-date in the local DRP db
# The Item Count data is put into Pandas directly and is not stored in the DRP db
def generate_reports(coll_rows, itct_filepath):

    logging.debug("generating reports")

    df_coll = pd.DataFrame(coll_rows)
    df_coll.columns = ["coll_uuid", "Community", "Collection"]
    logging.debug(f"Collections added to dataframe: {len(df_coll)}")


    df_itct = pd.read_csv(itct_filepath, header=None, sep=cfg.data_in_field_sep)

    assert (len(df_itct.columns) == 4), \
        f"{itct_filepath.name} has wrong number of columns"

    assert (len(df_itct) > 1), f"{itct_filepath.name} has no rows"

    df_itct.columns = ['coll_uuid', 'Year', 'Month', 'Item_Count']

    logging.debug(f"Item counts added to dataframe: {len(df_itct)}")

    df_itct.drop(columns=['Year', 'Month'], inplace=True)

    #df = pd.merge(df_coll, df_itct, how='left', on=['coll_uuid'], sort=False)
    df = pd.merge(df_coll, df_itct, how='outer', on=['coll_uuid'], sort=False)
    df['Community'] = df['Community'].fillna('unknown--')
    df['Collection'] = df['Collection'].fillna('--unknown--')
    df['Item_Count'] = df['Item_Count'].fillna(0)
    df.drop(columns=['coll_uuid'], inplace=True)
    df.set_index(['Community', 'Collection'], inplace=True)
    df = df.astype({'Item_Count': 'int64'})
    df.sort_index(inplace=True)

    #add column total
    sums =  df.sum(numeric_only=True, axis=0)   #this is a Series
    sums.name = ("Total", "")
    df = df.append(sums)

    now = datetime.now()
    stem = f"{cfg.rpt_basename}-{now.strftime('%Y%m%d')}"
    logging.debug(f"stem: {stem}")

    drp.write_rpts(df, cfg.rpt_formats, cfg.rpts_out_dirpath, stem, now.year)

    logging.info("Report creation complete.")


main((argv[1:]))
