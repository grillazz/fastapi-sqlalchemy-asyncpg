DROP DATABASE IF EXISTS devdb;
CREATE DATABASE devdb;
\connect merchantcenter;
CREATE SCHEMA shakespeare;

DROP DATABASE IF EXISTS testdb;
CREATE DATABASE testdb;
\connect merchantcenter;
CREATE SCHEMA shakespeare;
