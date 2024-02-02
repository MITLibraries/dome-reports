import csv


#list of SQL update commands
cmds = []

with open('coll-2109.csv', 'r') as f:
    reader = csv.reader(f, delimiter = '|')
    for row in reader:
        cmds.append(f"UPDATE Collection SET handle = '{row[4]}' WHERE uuid = '{row[0]}';")

with open('coll-handle-script.sql', 'w+') as s:
    for cmds in cmds:
        s.write('%s\n' %cmds)


