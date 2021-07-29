# drp/shared/config.py
import logging

from dataclasses import dataclass
from pathlib import Path
from sys import stdout


@dataclass
class ReportFormats:
    SCREEN:               bool = False
    ASCII:                bool = False
    CSV:                  bool = False
    HTML:                 bool = False
    MARKDOWN:             bool = False
    XLSX:                 bool = False

    def set_from_codes(self, codes):

        self.SCREEN = self.ASCII = self.CSV = self.HTML = \
                      self.MARKDOWN = self.XLSX = False

        for c in codes:
            if c == 's':
                self.SCREEN = True
            elif c == 'a':
                self.ASCII = True
            elif c == 'c':
                self.CSV = True
            elif c == 'h':
                self.HTML = True
            elif c == 'm':
                self.MARKDOWN = True
            elif c == 'x':
                self.XLSX = True
            else:
                logging.error("Error setting report format, code " + c)
                raise ValueError(f"Invalid  rpt fmt code '{c}'")


@dataclass
class Configuration:
    version:                    str

    log_file_level:             int
    log_console_level:          int
    log_file_append:            bool

    skip_ingest:                bool
    data_in_file_ext:            str
    data_in_field_sep:           str
    data_in_filename_filters:    tuple[str, ...]

    skip_output:                bool
    rpt_formats:                ReportFormats
    rpt_year:                   int
    rpt_fullname:               str
    rpt_basename:               str

    drp_dirpath:                Path
    shared_dirpath:             Path
    db_filepath:                Path
    rpt_dirpath:                Path
    data_in_dirpath:            Path
    data_done_dirpath:          Path
    rpts_out_dirpath:           Path


def log_init(logfilepath, filelog_level, consolelog_level, append):
    logging.basicConfig(level=filelog_level,
                        format='[%(asctime)s] %(levelname)s : %(message)s',
                        filename=logfilepath,
                        filemode= ('a' if append else 'w'))
    console = logging.StreamHandler(stream=stdout)
    console.setLevel(consolelog_level)
    console.setFormatter(logging.Formatter('%(levelname)s : %(message)s'))
    logging.getLogger('').addHandler(console)

#end of file
