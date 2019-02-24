# UDACITY Catalog App Project - Nils Steffensen

This Python script is an assignment part of the Full Stack Developer Nonadegree from Udacity, being submitted by Nils Steffensen.

## Pre-requiste setup

### Virtual Machine
If using Vagrant, download the VM configuration:
  * Download and unzip this file: https://s3.amazonaws.com/video.udacity-data.com/topher/2018/April/5acfbfa3_fsnd-virtual-machine/fsnd-virtual-machine.zip. This will give you a directory called FSND-Virtual-Machine.
  * cd to this directory, then to the sub-directory "vagrant".
  * Start the virtual machine by using the "vagrant up" command, and log in to it using "vagrant ssh" and cd to /vagrant.  Your file share is located there.

### Set up the database: 

**Create Database**
In psql, create the database:
```
create database catacity;
```

**Create Tables**

(1) Category table
```
CREATE TABLE category(
  id serial PRIMARY KEY,
  name VARCHAR (80) NOT NULL
);
```
(2) User table (named acct because in PostreSQL the keyword “user” is reserved and cannot be used as a table name without convolutions.)
```
CREATE TABLE acct(
  id serial PRIMARY KEY,
  name VARCHAR (80) NOT NULL,
  email VARCHAR (250) UNIQUE NOT NULL
);
```
(3) Item table
```
CREATE TABLE item(
  id serial PRIMARY KEY,
  title VARCHAR (80) NOT NULL,
  description VARCHAR (250),
  category_id integer NOT NULL REFERENCES category (id),
  acct_id integer NOT NULL REFERENCES acct (id)
);
```

**Optional step: Erase data from existing database**
If you have alread run the project but wish to reset to the original seed database, first manually wipe the tables.  In psql execute:
```
TRUNCATE item, acct, category;
```

** Seed the database
Run the python script __catacity_seed_database.py__
