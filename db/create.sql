DROP DATABASE IF EXISTS devdb;
CREATE DATABASE devdb;
\connect devdb;
CREATE SCHEMA shakespeare;

DROP DATABASE IF EXISTS testdb;
CREATE DATABASE testdb;
\connect testdb;
CREATE SCHEMA shakespeare;
