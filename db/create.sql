\connect devdb;
CREATE SCHEMA shakespeare;
CREATE SCHEMA happy_hog;
CREATE SCHEMA scheduler;

DROP DATABASE IF EXISTS testdb;
CREATE DATABASE testdb;
\connect testdb;
CREATE SCHEMA shakespeare;
CREATE SCHEMA happy_hog;
CREATE SCHEMA scheduler;
