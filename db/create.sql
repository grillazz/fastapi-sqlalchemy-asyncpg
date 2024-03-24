\connect devdb;
CREATE SCHEMA shakespeare;
CREATE SCHEMA happy_hog;

DROP DATABASE IF EXISTS testdb;
CREATE DATABASE testdb;
\connect testdb;
CREATE SCHEMA shakespeare;
CREATE SCHEMA happy_hog;
