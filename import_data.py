import getopt
import datetime
import calendar
import sqlite3
import csv
import logging
import logging.config
import glob
import shutil

from sys import argv, exit
from contextlib import closing
from os import path

"""
import Postgres extract tsv data to SQLite

    To be processed, import files are place in the imports subdirectory
    This application will determine the type from the file name
    and determine the proper processing order by type, year and month.
    Note that the scope of the SQLite database is to report the various
    states of Dome over time, and so retains all references even if they
    might be deleted in Dome (which probably doesn't happen).

"""

CONFIG = {
    'imports_dirpath' : './imports/',
    'completed_dirpath' : './imports_complete/',
    'db_filepath' : 'drp.db'
}

def main(argv):

    # Configure the logging system
    #log_file_path = path.join(path.dirname(path.abspath(__file__)), 'logs/drplog.config')
    #logging.config.fileConfig(log_file_path)

    logging.config.fileConfig('logs/drplog2.config')
    logging.info("start of import")

    # Commandline options
    try:
      opts, args = getopt.getopt(argv, "hi:c:d:", ["importdir=", "completedir=",
                                 "database="])
    except getopt.GetoptError:
      print_help()
      exit(2)

    for opt, arg in opts:
      if opt in ("-h", "--help"):
        print_help()
        exit(0)
      elif opt in ("-i", "--importdir"):
        CONFIG['imports_dirpath'] = arg
      elif opt in ("-c", "--completedir"):
        CONFIG['completed_dirpath'] = arg
      elif opt in ("-d", "--database"):
        CONFIG['db_filepath'] = arg

    logging.info(f"Starting import to {CONFIG['db_filepath']} from {CONFIG['imports_dirpath']}")

    # determine file contents in the imports directory
    comm_imports = get_imports_by_type("comm-????.tsv")
    coll_imports = get_imports_by_type("coll-????.tsv")
    itc_imports = get_imports_by_type("itc-????.tsv")

    # process the import files
    try:
      with closing(sqlite3.connect(CONFIG['db_filepath'])) as conn:
        with closing(conn.cursor()) as cursor:

          [import_containers(conn, cursor, "Community", fp) \
            for fp in comm_imports] 
          [import_containers(conn, cursor, "Collection", fp) \
            for fp in coll_imports] 
          [import_itemcounts(conn, cursor, fp) for fp in itc_imports] 

    except sqlite3.Warning as w:
      logging.warning("Import comms: SQLite Warning: " + str(w))
      #commit or rollback??
    except sqlite3.Error as e:
      logging.error("Import comms: SQLite Error: " + str(e))
      #conn.rollback()
      exit(2)

    logging.info("Import processing completed")
    logging.shutdown()


# import files are obtained on the basis of presence 
# in the designated directory
def get_imports_by_type(namefilter):

    filepaths = glob.glob(path.join(CONFIG['imports_dirpath'], namefilter))
    #filenames = [path.basename(p) for p in paths]
    if len(filepaths) > 1: filepaths.sort() 

    # if len(filenames) > 0:
      # print("len of filenames list: " + str(len(filenames)))
      # print("first filename: " + filenames[0])
    return filepaths


# used at the start of the functions "import_..."
# reads the data file into a list of tab-delimited values
def start_import(cursor, tsv):

    logging.info(f"processing {tsv}.")

    # check if filename is listed as having been processed
    c = cursor.execute("SELECT COUNT(*) FROM FilesProcessed WHERE name = ?",
        (path.basename(tsv), )).fetchall()
    if c[0][0] > 0:
      logging.info(f"{tsv} already processed. ")
      shutil.move(tsv, CONFIG['completed_dirpath'])
      logging.info(f"{tsv} moved to completed folder")
      return None

    with open (tsv, 'r') as f:
      #for irow in csv.reader(f,delimiter='\t'):
      irows = [irow for irow in csv.reader(f, delimiter='\t')]
      # print(f"count of rows in {tsv}: " + str(len(irows))) 
    return irows


# import either community or container
# param 'table' is used for both messages and the table name 
def import_containers(conn, cursor, table, tsv):

    irows = start_import(cursor, tsv)
    if irows is None:
        return

    if len(irows) == 0:
      logging.error(f"{tsv} is empty; Not correct for Community or Collection")
      return

    if table == "Community":
      query = \
      f"INSERT INTO Community(uuid, name, short_name) VALUES (?, ?, ?)" 
    else:  
      query = \
      f"INSERT INTO Collection(uuid, comm_uuid, name, short_name) VALUES (?, ?, ?, ?)" 

    #get all comm uuids from db
    db_rows = cursor.execute("SELECT uuid FROM " + table).fetchall()
    logging.debug(table + " row count: " + str(len(db_rows)))

    if len(db_rows) == 0:
      logging.info("db container table is empty; loading all tsv rows")
      cursor.executemany(insert_query, irows)
    else:
      # filtering tsv for new rows
      db_uuids = set()

      for db_row in db_rows:
        # print(db_row[0])
        db_uuids.add(db_row[0])

      logging.debug("uuid set size: " + str(len(db_uuids)))

      nadded = 0
      for irow in irows:
        if irow[0] not in db_uuids:
          cursor.execute(insert_query, irow)
          nadded += 1
          # print("file row inserted: " + str(irow))

      logging.info(f"Count of added containers: {nadded}")

    cursor.execute("INSERT INTO FilesProcessed(name, timestamp) VALUES (?, CURRENT_TIMESTAMP);",        (path.basename(tsv), ))
    logging.info("recorded processed tsv")
    conn.commit()
    logging.info("committed data from " + path.basename(tsv))
    logging.info(f"Processed {tsv} with {nadded} new rows added")

    shutil.move(tsv, CONFIG['completed_dirpath'])
    logging.info(f"moved {tsv} to completed folder")


def import_itemcounts(conn, cursor, tsv):

    irows = start_import(cursor, tsv)
    if irows is None:
        return

    if len(irows) == 0:
      logging.info(f"{tsv} is empty; nothing to import")
      return

    insert_query = "INSERT INTO Monthly_Item_Count" + \
        "(coll_uuid, year, month, item_count) VALUES (?, ?, ?, ?);"
    cursor.executemany(insert_query, irows)
    logging.info(f"Inserted {len(irows)}") 

    cursor.execute("INSERT INTO FilesProcessed(name, timestamp) VALUES (?, CURRENT_TIMESTAMP);",        (path.basename(tsv), ))
    logging.info("recorded processed tsv")
    conn.commit()
    logging.info("committed data from " + path.basename(tsv))
    logging.info(f"Processed {tsv}")

    shutil.move(tsv, CONFIG['completed_dirpath'])
    logging.info(f"moved {tsv} to completed folder")


def print_help():
    print("Usage:  python3 import_data.py -h(elp) -f <file> -d <test_db>")


main((argv[1:]))
