FROM python:3.10-alpine

RUN apk add --no-cache sqlite

WORKDIR /db

# Copy the SQL file containing the schema and initial data
COPY ./db/. .

# Keep the container running and initialize the database if it doesn't exist
CMD ["/bin/sh", "-c", "if [ ! -f sqlite_app.db ]; then touch sqlite_app.db && sqlite3 sqlite_app.db < init.sql; fi && tail -f /dev/null"]