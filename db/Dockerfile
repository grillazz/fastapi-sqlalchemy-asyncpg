# pull official base image
FROM postgres:14-alpine

# run create.sql on init
ADD create.sql /docker-entrypoint-initdb.d

WORKDIR /home/gx/code

COPY shakespeare_chapter.sql /home/gx/code/shakespeare_chapter.sql
COPY shakespeare_work.sql /home/gx/code/shakespeare_work.sql
COPY shakespeare_wordform.sql /home/gx/code/shakespeare_wordform.sql
COPY shakespeare_character.sql /home/gx/code/shakespeare_character.sql
COPY shakespeare_paragraph.sql /home/gx/code/shakespeare_paragraph.sql
COPY shakespeare_character_work.sql /home/gx/code/shakespeare_character_work.sql