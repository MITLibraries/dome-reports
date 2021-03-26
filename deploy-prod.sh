#!/usr/bin/zsh
# shell script to build production deployment directory

# default location is relative to the pwd, i.e. the top level git directory
DEFAULT_DIR="../prod"

if ! [ -z "$1" ]; then
     PROD_DIR="$1"
else
     PROD_DIR=$DEFAULT_DIR
fi

if [ -d "$PROD_DIR" ]; then
    if [ "$(ls -A $PROD_DIR)" ]; then
        echo "ERROR: $PROD_DIR  directory is not empty. Exiting script."
        exit 1
    fi
else
    if ! mkdir $PROD_DIR; then
        echo "ERROR CREATING DIRECTORY: $PROD_DIR  Exiting script."
        exit 1
    else
        echo "Created $PROD_DIR directory"
    fi
fi

SUB_DIRS=(imports imports_completed initial_load reports)

for subdir in $SUB_DIRS
do
    if ! mkdir "$PROD_DIR/$subdir"; then
        echo "ERROR CREATING DIRECTORY: $PROD_DIR/$subdir  Exiting script."
        exit 1
    else
        echo "Created subdirectory: $subdir"
    fi
done

if ! cp -R logs $PROD_DIR; then
    echo "ERROR COPYING DIRECTORY logs   Exiting script."
    exit -1
else
    echo "Copied subdirectory logs"
fi

if ! cp -R postgres $PROD_DIR; then
    echo "ERROR COPYING DIRECTORY postgres   Exiting script."
    exit -1
else
    echo "Copied subdirectory postgres"
fi

if ! cp -R sql $PROD_DIR; then
    echo "ERROR COPYING DIRECTORY sql   Exiting script."
    exit -1
else
    echo "Copied subdirectory sql"
fi

if ! cp {*.py,*.sh} $PROD_DIR; then
    echo "ERROR COPYING FILES to $PROD_DIR  Exiting script."
    exit 1
else
    echo "Files copied"
fi


DB_NAME="drp-prod.db"

if ! sqlite3 $PROD_DIR/$DB_NAME < $PROD_DIR/sql/db-ddl.sql; then
    echo "ERROR CREATING SQLITE3 DB  $PROD_DIR/$DB_NAME  Exiting script."
    exit 1
else
    echo "Created database $DB_NAME"
fi

echo "\ndeploy-prod script completed"
