-- Run this file from the command line using:
--     psql -d catacity -a -f db_seed.sql

/* Delete contents from all tables */
TRUNCATE item, acct, category;

/* Seed the [category] table */
INSERT INTO category (id, name) VALUES (1, 'Albums');
INSERT INTO category (id, name) VALUES (2, 'Books');
INSERT INTO category (id, name) VALUES (3, 'Movies');

/* Seed the [acct] table */
INSERT INTO acct (id, name, email) VALUES (1, 'Alice', 'alice@sample.com');
INSERT INTO acct (id, name, email) VALUES (2, 'Bob', 'bob@sample.com');
INSERT INTO acct (id, name, email) VALUES (3, 'Dave', 'dave@sample.com');
INSERT INTO acct (id, name, email) VALUES (4, 'Evaline', 'evaline@sample.com');

/* Seed the [item] table */
INSERT INTO item (id, title, description, category_id, acct_id)
	VALUES ( 							1,	'White Album',
			 								'A Beatles album which is white',
	(SELECT id FROM category WHERE name = 	'Albums'),
	(SELECT id FROM acct WHERE name = 		'Alice'));

INSERT INTO item (id, title, description, category_id, acct_id)
	VALUES ( 							2,	'Hitchhikers Guide',
			 								'An quirky book by Douglas Adams',
	(SELECT id FROM category WHERE name = 	'Books'),
	(SELECT id FROM acct WHERE name = 		'Alice'));

INSERT INTO item (id, title, description, category_id, acct_id)
	VALUES ( 							3,	'Avatar',
			 								'Dances With Wolves in space!',
	(SELECT id FROM category WHERE name = 	'Movies'),
	(SELECT id FROM acct WHERE name = 		'Bob'));

INSERT INTO item (id, title, description, category_id, acct_id)
	VALUES ( 							4,	'The Hobbit',
			 								'A prequel to the Lord of the Rings saga.',
	(SELECT id FROM category WHERE name = 	'Books'),
	(SELECT id FROM acct WHERE name = 		'Dave'));

INSERT INTO item (id, title, description, category_id, acct_id)
	VALUES ( 							5,	'Rambo',
			 								'Thoughtful treatise on the human experience.',
	(SELECT id FROM category WHERE name = 	'Movies'),
	(SELECT id FROM acct WHERE name = 		'Evaline'));

INSERT INTO item (id, title, description, category_id, acct_id)
	VALUES ( 							6,	'Black Album',
			 								'Album by JayZ which is black',
	(SELECT id FROM category WHERE name = 	'Albums'),
	(SELECT id FROM acct WHERE name = 		'Bob'));

INSERT INTO item (id, title, description, category_id, acct_id)
	VALUES ( 							7,	'Gray Album',
			 								'Remix of the Black and White albums by Danger Mouse',
	(SELECT id FROM category WHERE name = 	'Albums'),
	(SELECT id FROM acct WHERE name = 		'Bob'));

/* Display table contents on the command line */
SELECT * FROM category;
SELECT * FROM acct;
SELECT * FROM item;
