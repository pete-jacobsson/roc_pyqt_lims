### All in Ubuntu Command line:

## Pull postgres from docker hub:
docker pull postgres


## Create the docker volume to get persistent data:
docker volume create pyqt_lims_pd


## Run the container. Map to 54321 in case 5432 occupied
docker run --name pyqt_lims_db \
  -e POSTGRES_PASSWORD= \
  -v pyqt_lims_pd:/var/lib/postgresql/data \
  -p 54321:5432 \
  -d postgres


## Getting rid of the container
docker rm pyqt_lims_db


## Now you have a PostgreSQL container running with persistent storage. You can connect to it using any PostgreSQL client, including the command-line tool psql:

docker exec -it pyqt_lims_db psql -U postgres

#### Check connection
postgres-# \conninfo

#### Creating the pyqt_lims_devs user:
_This user will be used to set up the DB for the LIMS_
CREATE USER pyqt_lims_devs WITH PASSWORD 'NOPE';

#### Creating the DB
CREATE DATABASE pyqt_lims_database;

_Gives the devs user privilidges for building up the DB_
GRANT ALL PRIVILEGES ON DATABASE pyqt_lims_database TO pyqt_lims_devs;
\c pyqt_lims_database


GRANT ALL ON SCHEMA public TO your_new_username;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO pyqt_lims_devs;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO pyqt_lims_devs;

ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO pyqt_lims_devs;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO pyqt_lims_devs;



