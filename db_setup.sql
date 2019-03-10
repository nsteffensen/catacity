-- Run this file from the command line using:
--     psql -d catacity -a -f db_setup.sql

CREATE TABLE category(
  id serial PRIMARY KEY,
  name VARCHAR (80) NOT NULL
);

/*
User table (named acct because in PostreSQL the 
keyword “user” is reserved and cannot be used as 
a table name without convolutions.)
*/
CREATE TABLE acct(
  id serial PRIMARY KEY,
  name VARCHAR (80) NOT NULL,
  email VARCHAR (250) UNIQUE NOT NULL
);

CREATE TABLE item(
  id serial PRIMARY KEY,
  title VARCHAR (80) NOT NULL,
  description VARCHAR (250),
  category_id integer NOT NULL REFERENCES category (id),
  acct_id integer NOT NULL REFERENCES acct (id)
);
