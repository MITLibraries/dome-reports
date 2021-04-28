#!/usr/bin/sh
# bash script to remotely query Dome's Postgres DB
# for monthly report data

YYMM=`date +"%y%m"`
COMM='comm-'$YYMM'.tsv'
COLL='coll-'$YYMM'.tsv'
ITC='itc-'$YYMM'.tsv'

SERVER_NAME=''

#    Note:  these psql calls require manually entered password
#

#    creates tab-delimited rows
#    no headers or footer ( -t )
#
#    to import into sqlite database: 
#        >sqlite3 drp-prod.db 
#
#
#    then run these commands at the sqlite3 command line
#        PRAGMA foreign_keys = ON
#
#        .mode tabs 
#

# use the Postgres default separator - the vertical bar '|'
# the metadata_field_id can vary from one DSpace implementation to another
# the -t flag in psql suppresses column headers and footers

#  -- extract communities

psql -h $SERVER_NAME -U dspace -d dome6prod --no-align -t -c 'SELECT comm.uuid, mv.text_value as name, mv.text_value as short_name FROM community comm INNER JOIN metadatavalue mv ON comm.uuid = mv.dspace_object_id WHERE mv.metadata_field_id = 64;' > $COMM


#  -- extract collections

psql -h $SERVER_NAME -U dspace -d dome6prod --no-align -t -c 'SELECT col.uuid, c2c.community_id, mv.text_value as name, mv.text_value as short_name FROM community2collection c2c INNER JOIN collection col ON c2c.collection_id = col.uuid INNER JOIN metadatavalue mv ON col.uuid = mv.dspace_object_id WHERE mv.metadata_field_id = 64;' > $COLL


#  --extract counts

psql -h $SERVER_NAME -U dspace -d dome6prod --no-align -t -c 'SELECT coll.uuid, EXTRACT(YEAR FROM CURRENT_TIMESTAMP), EXTRACT(MONTH FROM CURRENT_TIMESTAMP), COUNT(item.uuid) FROM collection coll INNER JOIN item ON coll.uuid = item.owning_collection WHERE item.in_archive = true and item.withdrawn = false  GROUP BY coll.uuid;' > $ITC
