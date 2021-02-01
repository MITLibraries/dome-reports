import getopt
import datetime
import calendar
import sqlite3
import pandas as pd
import numpy as np
from sys import argv, exit
#from xhtml2pdf import pisa
from contextlib import closing


def main(argv):

    month = year = 0
    fmts = ''
    ASCII = True  #default
    CSV = False
    HTML = False
    MARKDOWN = False
    XLSX = False

    try:
        opts, args = getopt.getopt(argv,"hm:y:f:",["month=","year=","fmts="])
    except getopt.GetoptError:
        print_help()
        exit(2)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print_help()
            exit()
        elif opt in ("-y", "--year"):
            year = int(arg)
        elif opt in ("-f", "--fmts"):
            fmts = arg
            ASCII = ('a' in fmts)
            CSV = ('c' in fmts)
            HTML = ('h' in fmts)
            MARKDOWN = ('m' in fmts)
            XLSX = ('x' in fmts)

    #print(f"for {year} with formats {fmts}")

    today = datetime.date.today()

    if year == 0:
        #default to year of previous month
        if today.month == 1:
            year = today.year - 1
        else:
            year = today.year

    print("Extracting and formatting Dome Collection Item Count report")
    print(f"for year {year}")

    query1 = ("SELECT comm.name as Community, coll.name as Collection, month, item_count "
          "FROM Community comm JOIN Collection coll ON comm.uuid = coll.comm_uuid "
          "JOIN ItemCount itc ON coll.uuid = itc.coll_uuid "
          "WHERE year = ? "
          "ORDER BY coll.comm_uuid, coll.name;")

    with closing(sqlite3.connect("drp_db2")) as conn:
        with closing(conn.cursor()) as cursor:
            rows = cursor.execute(query1, (year,)).fetchall()
    print(f'count of rows: {len(rows)}')

    if len(rows) == 0:
        print(f"No data for year {year}")
        exit(1)

    df = pd.DataFrame(rows)

    #print(df);

    df.columns = ["Community", "Collection", "Month", "Count"]

    #pt = df.pivot_table( index=[0], values=[2], columns=[1], aggfunc=max)
    pt = df.pivot_table( index=["Community", "Collection"],
              values=["Count"], columns=["Month"], fill_value=0, aggfunc=max)

    #extract column integers (will these always be sorted?)
    #i.e. the exact months in query result, skipping months with no data
    ar_mo_int = [ j for i, j in pt.columns.to_flat_index().to_list()]
    #get array of corresponding months
    pt.columns = [calendar.month_abbr[i] for i in ar_mo_int]

    outfilename = f'drp_col_it_{year}-{month}'

    if ASCII:
        with open(f'{outfilename}.txt', 'w') as ascii_out:
            table = pt.to_string(index = True)
            ascii_out.write(add_common_header(table, year))
    if CSV:  #no headers??
        pt.to_csv(f'{outfilename}.csv', index = True)
    if HTML:
        with open(f'{outfilename}.html', 'w') as html_out:
            html = pt.to_html().replace(" style=\"text-align: right;\"", "", 1)
            html_out.write(format_html(html, year))
    if MARKDOWN:
        with open(f'{outfilename}.md', 'w') as md_out:
            table = pt.to_markdown(index = True)
            md_out.write(format_markdown(table, year))
    if XLSX:
        pt.to_excel(f'{outfilename}.xlsx', index = True)

    #for dev
    print(add_common_header(pt.to_string(index = True), year))

    print("\nend of program")


def print_help():
    print('Usage: drp.py -h(elp) -y <year> -f <formats>')
    print('where a = ascii (default), c = csv, h = html, m=markdown')
    print('default year will be the calendar year of the previous month')


"""  currently not used
pdf = open("drp2.pdf", "w+b")
pisa_status = pisa.CreatePDF(html, dest=pdf)
pdf.close()
print("pisa_status: " + str(pisa_status.err));
"""

def add_common_header(table, year):
    return f"""\n    MIT Libraries  -- dome.mit.edu\n
    Monthly Reports -- {year}\n    Collection Item Counts\n\n""" \
    + table + "\n"

# community and collection are presented tuple
# tabulate and panda docs don't offer an option to break up as columns
# may be better to write a custom formatter here
def format_markdown(table, year):
    return "# MIT Libraries  -- dome.mit.edu" \
        + f"\n## Monthly Reports -- {year}\n## Collection Item Counts\n\n" \
        + table + "\n"


def format_html(table, year):

    template_top = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <title>dome.mit.edu - Collection Item Counts Monthly Report</title>

    <style>
    body {{
    font-family: Garamond, Arial;
    }}

    h1 {{
    font-family: Garamond, Arial;
    font-weight: normal;
    margin-left: 40px;
    }}

    table {{
    border-collapse: collapse;
    margin-left: 50px;
    }}

    table tbody tr th {{
    font-family: "Times New Roman", Times;
    text-align: left;
    padding: 0px 5px;
    }}

    table tbody tr td {{
    text-align: right;
    padding: 0px 3px;
    }}

    </style>
    </head>
    <body>

    <h2>MIT Libraries  -- dome.mit.edu</h2>
    <h1>Monthly Reports -- {year}</h1>
    <h1>Collection Item Counts</h1>

    """

    template_bottom = """
    </body>
    </html>

    """

    return template_top + table + template_bottom

main((argv[1:]))
