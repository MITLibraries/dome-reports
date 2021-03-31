#!/usr/bin/sh
# bash script to query Dome's Postgres DB
# for monthly report data

YYMM=`date +"%y%m"`
COMM='comm-'$YYMM'.tsv'
COLL='coll-'$YYMM'.tsv'
ITC='itc-'$YYMM'.tsv'

#    Note:  these psql calls are not configured
#           for a remote connection
#


#    creates tab-delimited rows
#    no headers or footer ( -t )
#
#    to import into sqlite, create a test database:
#        >sqlite3 test-drp-4.db 
#
#
#    then run these commands at the sqlite3 command line
#        PRAGMA foreign_keys = ON
#
#        .mode tabs 
#

#  -- extract communities
# preliminary version where tabs are specified
# this does not work on the target server, so the next version below
# settles for the default vertical bar char '|'
# the metadata_field_id can vary from one DSpace implementation to another
# the -t flag in psql suppresses column headers and footers

sudo -u postgres psql -d dspace -AF \$'\t' --no-align -t -c 'SELECT comm.uuid, mv.text_value as name, mv.text_value as short_name FROM community comm INNER JOIN metadatavalue mv ON comm.uuid = mv.dspace_object_id WHERE mv.metadata_field_id = 64;' > $COMM

# working version using the Postgres default separator - the vertical bar '|'
sudo -u postgres psql -d dspace --no-align -t -c 'SELECT comm.uuid, mv.text_value as name, mv.text_value as short_name FROM community comm INNER JOIN metadatavalue mv ON comm.uuid = mv.dspace_object_id WHERE mv.metadata_field_id = 64;' > $COMM

#  -- extract collections
# here, the working version with the default field separator 

sudo -u postgres psql -d dspace --no-align -t -c 'SELECT col.uuid, c2c.community_id, mv.text_value as name, mv.text_value as short_name FROM community2collection c2c INNER JOIN collection col ON c2c.collection_id = col.uuid INNER JOIN metadatavalue mv ON col.uuid = mv.dspace_object_id WHERE mv.metadata_field_id = 64;' > $COLL


#  --extract counts
# here, the workiing version with the default field separator

sudo -u postgres psql -d dspace --no-align -t -c 'SELECT coll.uuid, EXTRACT(YEAR FROM CURRENT_TIMESTAMP), EXTRACT(MONTH FROM CURRENT_TIMESTAMP), COUNT(item.uuid) FROM collection coll INNER JOIN item ON coll.uuid = item.owning_collection WHERE item.in_archive = true and item.withdrawn = false  GROUP BY coll.uuid;' > $ITC

