This is the latest version of the dome reporting scripts

r_cicmits - collection item count monthly time series

r_cicah - collection item count ad-hoc

Bill also says:

And just to note, in addition to annoyingly changing the names
of things, I changed the name of the item_count csv file:

itc.csv -> itct.csv

But this is also customizable in the config, see "data_in_filters"

removed imports directory, now called ?

cd /Users/carlj/Developer/Dome/DomeReports-2021-new/dome-reports

Enable python3 virtual environment:  'source venv391/bin/activate'

To run monthly reports, 'cd r_cicmts's directory and run 'python3 ./cicmts.py'

or just: python3 cicmts.py

  python3 ./cicmts.py
  python3 ./cicmts.py -h
  python3 ./cicmts.py -y 2021
  
  
+ For 2024 we are updating Pandas to version 2.2.0(?) as append() is now deprecated and we must use 'concat()' instead. We're also taking this as an opportunity to bump up the required Python version to 3.12.
