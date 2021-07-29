#drp/r_cicmts/config.py

# workaround to have access to
# the shared directory ../shared
from sys import path as syspath
from pathlib import Path
DRP_PATH = Path(__file__).parents[1]
syspath.append(str(DRP_PATH))
import shared.config as shared

import getopt
import logging

from datetime import datetime
from dataclasses import dataclass


# Here is the edited configuration: Make changes here!
def get_config():
    RPT_PATH = Path(__file__).parents[0]

    return shared.Configuration(
        version = '0.2.3',

        log_file_level = logging.INFO,
        log_console_level = logging.INFO,
        log_file_append = True,

        skip_ingest = False,
        data_in_file_ext = 'csv',
        data_in_field_sep = '|',

        data_in_filename_filters = ('comm-????.csv',
                                   'coll-????.csv',
                                   'itct-????.csv'),

        skip_output = False,
        rpt_formats = shared.ReportFormats(SCREEN = True, ASCII = True),
        rpt_year = datetime.now().year,
        rpt_fullname = 'Monthly Collections Item Counts Time Series',
        rpt_basename = 'dome-cicmts',

        drp_dirpath = DRP_PATH,
        shared_dirpath = DRP_PATH / 'shared',
        db_filepath = DRP_PATH / 'db' / 'drp.db',

        rpt_dirpath = RPT_PATH,
        data_in_dirpath = RPT_PATH / 'data_in',
        data_done_dirpath = RPT_PATH / 'data_done',
        rpts_out_dirpath = RPT_PATH / 'rpts_out',
    )


def get_commandline_options(argv, cfg):
    opts, args = getopt.getopt(argv, "hkpi:o:f:y:d:",
                 ["help",
                  "skip_ingest",
                  "skip_rpts",
                  "data_in_dir_path=",
                  "rpts_dir_path=",
                  "rpt_fmts=",
                  "rpt_year=",
                  "db_file_path="])

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print(get_help_text())
            exit(0)
        elif opt in ("-k", "--skip_ingest"):
            cfg.skip_ingest = True
        elif opt in ("-i", "--data_in_dir_path"):
            cfg.data_in_dirpath = Path(arg).resolve()
            logging.debug(f"New input dir: {cfg.data_in_dirpath}")
            assert Path.is_dir(cfg.data_in_dirpath), \
                   f"{cfg.data_in_dirpath} is not directory or doesn't exist"
        elif opt in ("-p", "--skip_rpts"):
            cfg.skip_output = True
        elif opt in ("-o", "--out_dir_path"):
            cfg.rpts_out_dirpath = Path(arg).resolve()
            logging.debug(f"New output dir: {cfg.rpts_out_dirpath}")
            assert Path.is_dir(cfg.rpts_out_dirpath), \
                   f"{cfg.rpts_out_dirpath} is not directory or doesn't exist"
        elif opt in ("-f", "--fmts"):
            cfg.rpt_formats.set_from_codes(arg)   #can raise ValueError
            logging.debug(f"Rpt formats set to: {arg}")
        elif opt in ("-y", "--year"):
            cfg.rpt_year = int(arg)
            logging.debug(f"Report year set to: {cfg.rpt_year}")
        elif opt in ("-d", "--db_file_path"):
            cfg.db_filepath = Path(arg).resolve()
            logging.debug(f"Database set to {cfg.db_filepath}")

    # no required options to validate

# validation is done once:
# after the config values are set *AND* are updated from the commandline
def validate_config(cfg):
    #db file
    if not cfg.db_filepath.is_file():
        raise ValueError(f"Specified database file {cfg.db_filepath} does not exist.")

    #data_in
    if not cfg.data_in_dirpath.exists:
        raise ValueError(f"Ingest dir {cfg.data_in_dirpath} does not exist")

    #data_done
    if not cfg.data_done_dirpath.exists:
        raise ValueError(f"Ingest dir {cfg.data_done_dirpath} does not exist")

    #rpts_out
    if not cfg.rpts_out_dirpath.exists():
        raise ValueError(f"Reports output dir {cfg.rpts_out_dirpath} does not exist")

    #rpt year
    if not 2020 <= cfg.rpt_year <= datetime.now().year:
        raise ValueError(f"Report year {cfg.rpt_year}  is not in range")

def get_help_text():
    return '''
    Usage:  python3 /path/to/rpt_cicts.py
       -h <--help>
       -k <--skip_ingest>
       -p <--skip_rpts>
       -i <--data_dir_path= ...>
       -o <--rpts_dir_path= ...>
       -f <--rpt_fmts= any combination of:
           s (Screen)
           a (ASCII)
           h (HTML)
           m (Markdown)
           x (Excel XLSX)>
       -y <--rpt_year= yyyy>
       -d <--db_file_path= ...>

    '''
# end of file
