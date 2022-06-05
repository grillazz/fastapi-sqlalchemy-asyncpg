# pull official base image
FROM postgres:14-alpine

# run create.sql on init
ADD create.sql /docker-entrypoint-initdb.d

WORKDIR /home/gx/code

COPY shakespeare_chapter.sql /home/gx/code/shakespeare_chapter.sql
COPY shakespeare_work.sql /home/gx/code/shakespeare_work.sql