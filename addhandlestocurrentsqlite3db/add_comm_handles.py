import csv


#list of SQL update commands
cmds = []

with open('comm-2109.csv', 'r') as f:
    reader = csv.reader(f, delimiter = '|')
    for row in reader:
        cmds.append(f"UPDATE Community SET handle = '{row[3]}' WHERE uuid = '{row[0]}';")

with open('comm-handle-script.sql', 'w+') as s:
    for cmds in cmds:
        s.write('%s\n' %cmds)


