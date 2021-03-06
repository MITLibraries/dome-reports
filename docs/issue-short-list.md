#### MIT Libraries - Dome Reports

## Short list of development issues

### Access

    - to Postgres DB from Server X
    - to Server X from the Reporting workstation 

### Notification during the running of the report process

    - logging is passive, but operational
    - OS X Notification Center - usability unknown
    - email - automation hurdles, except possibly Mutt; also security issues

### Testing

    - importance of not accidentally writing test data to SQLite
    - create test data for a full calendar year

### Backup

    - On each monthly run, backup the SQLite3 DB both locally and elsewhere

### Report formatting

    - PDF currently deferred

### Report distribution

    - default to email attachment, for a single one-page report
    - also possible:
      -  mounting files on a server
      -  Dome collection for reports
      -  content management system (doesn't exist for the MIT Libraries)

