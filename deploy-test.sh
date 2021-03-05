#!/usr/bin/sh
# shell script to build test deployment directory
# compatible with zsh

# default location is relative to the pwd, i.e. the top level git directory
DEFAULT_DIR="../test"

if ! [ -z "$1" ]; then
     TEST_DIR="$1"
else
     TEST_DIR=$DEFAULT_DIR
fi

if [ -d "$TEST_DIR" ]; then
    if [ "$(ls -A $TEST_DIR)" ]; then
        echo "ERROR: $TEST_DIR  directory is not empty. Exiting script."
        exit 1
    fi
else
    if ! mkdir $TEST_DIR; then
        echo "ERROR CREATING DIRECTORY: $TEST_DIR  Exiting script."
        exit 1
    else
        echo "Created $TEST_DIR directory"
    fi
fi

SUB_DIRS=(imports imports_completed initial_load logs reports)

for subdir in $SUB_DIRS
do
    if ! mkdir "$TEST_DIR/$subdir"; then
        echo "ERROR CREATING DIRECTORY: $TEST_DIR/$subdir  Exiting script."
        exit 1
    else
        echo "Created subdirectory: $subdir"
    fi
done

if ! cp -R postgres/ $TEST_DIR; then
    echo "ERROR COPYING DIRECTORY postgres   Exiting script."
    exit -1
else
    echo "Copied subdirectory postgres"
fi

if ! cp -R sql/ $TEST_DIR; then
    echo "ERROR COPYING DIRECTORY sql   Exiting script."
    exit -1
else
    echo "Copied subdirectory sql"
fi

if ! cp {*.py,*.sh} $TEST_DIR; then
    echo "ERROR COPYING FILES to $TEST_DIR  Exiting script."
    exit 1
else
    echo "Files copied"
fi


DB_NAME="drp-test-1.db"

if ! sqlite3 $TEST_DIR/$DB_NAME < $TEST_DIR/sql/db-ddl.sql; then
    echo "ERROR CREATING SQLITE3 DB  $TEST_DIR/$DB_NAME  Exiting script."
    exit 1
else
    echo "Created database $DB_NAME"
fi

echo "\ndeploy-prod script completed"
