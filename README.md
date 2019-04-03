# UDACITY Catalog App Project - Nils Steffensen

This Python script is an assignment part of the Full Stack Developer Nonadegree from Udacity, being submitted by Nils Steffensen.  It allows a user to log in with their Google account and save media items under the categories of Albums, Books or Movies.  An SQL script is available to populate sample items (obviously not under your account).

View a Category (the View link next to the Category name) in order to add new items.

## Pre-requiste setup

### Virtual Machine
If using Vagrant, download the VM configuration:
  * Download and unzip this file: https://s3.amazonaws.com/video.udacity-data.com/topher/2018/April/5acfbfa3_fsnd-virtual-machine/fsnd-virtual-machine.zip. This will give you a directory called FSND-Virtual-Machine.
  * cd to this directory, then to the sub-directory "vagrant".
  * Start the virtual machine by using the "vagrant up" command, and log in to it using "vagrant ssh" and cd to /vagrant.  Your file share is located there.
  * Clone this project into that directory.

### Set up the database: 

Only once, run the following at the command line:
```
psql -a -f db_create.sql
```
```
psql -d catacity -a -f db_setup.sql
```
The database begins empty but a script is provided to seed it.  WARNING, running the script deletes all existing data first.  Any time you wish to delete the ENTIRE database contents and replace with seed data, run the following:
```
psql -d catacity -a -f db_seed.sql
```
Just for reference, if you wish to destroy the entire database (you will have ro rerun the steps above to run the app), run the following:
```
psql -a -f db_destroy.sql
```

### Create a Google Client ID
* To get a client ID, follow directions at https://developers.google.com/identity/sign-in/web/server-side-flow.
* Save the client information in a file named "client_secrets.json" in the project directory.
* In login.html replace the client ID with your own.

### Run the app
Run the app from the command line within vagrant:
```
python app_catacity.py
```
In a web browser navigate to http://localhost:5000/.


