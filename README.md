Project from COMS W4111 - Intro to Databases by professor Luis Gravano.
Authors: Omer Mustel, Daina Lee





The project is a food review app, and unlike most apps, users review specific foods instead of restaurants.
There is a flask server that connect between a front-end and a psql database that sits in google cloud platform.


PostgreSQL Schema:

CREATE TABLE Foods(

fid 			   CHAR(7),
name 			   VARCHAR(20) NOT NULL,
price 			   REAL CHECK(price > 0),
category 		   VARCHAR(25) NOT NULL,
spicy_level 	   	   REAL CHECK(spicy_level >= 0),
vegan 			   BOOLEAN NOT NULL,
vegetarian 	    	   BOOLEAN NOT NULL,
main_ingridient 	   VARCHAR(100),
PRIMARY KEY(fid)

);

CREATE TABLE Users(
user_name 	VARCHAR(20),
name 		   VARCHAR (20) NOT NULL,
email 		   VARCHAR (25) NOT NULL,
sex    		   CHAR (1),

UNIQUE(email),
PRIMARY KEY(user_name)

);

CREATE TABLE Reviews(
rid CHAR(7),
rating REAL CHECK(rating >= 0 AND rating <= 5),
picture VARCHAR(100),
comment VARCHAR(450),

PRIMARY KEY(rid)

);


CREATE TABLE Allergies(

allergy_name VARCHAR(30),
PRIMARY KEY(allergy_name)
);

CREATE TABLE Restaurants (
res_id CHAR(7),
name VARCHAR(45) NOT NULL,
capacity INTEGER CHECK(capacity > 0),
open_time TIME,
close_time TIME,
PRIMARY KEY(res_id)

);

CREATE TABLE Locations(
GM_link VARCHAR(100),
street VARCHAR (40),
zip_code VARCHAR (5),
floor VARCHAR (3),

PRIMARY KEY(GM_link)

);

CREATE TABLE Found_At(
since DATE, 
GM_link VARCHAR (100) NOT NULL,
res_id CHAR(7) NOT NULL,

PRIMARY KEY (GM_link),
FOREIGN KEY (GM_link)
REFERENCES Locations,
FOREIGN KEY (res_id)
REFERENCES Restaurants
);

CREATE TABLE Rest_Allergies (
sterility BOOLEAN CHECK (sterility = TRUE OR  sterility = FALSE),
allergy_name VARCHAR(30),
GM_link VARCHAR(100),

PRIMARY KEY(GM_link, allergy_name),
FOREIGN KEY(Allergy_name)
REFERENCES Allergies,
FOREIGN KEY (GM_link)
REFERENCES Found_At (GM_link)
);


CREATE TABLE Sensitive_To(
user_name VARCHAR(20),
allergy_name VARCHAR(30),

PRIMARY KEY(user_name, allergy_name),
FOREIGN KEY(user_name) REFERENCES Users,
FOREIGN KEY(allergy_name) REFERENCES Allergies
);









CREATE TABLE Food_Contain(
fid CHAR(7),
allergy_name  VARCHAR(30),

PRIMARY KEY(allergy_name, fid),
FOREIGN KEY(allergy_name) REFERENCES Allergies,
FOREIGN KEY(fid) REFERENCES Foods

);


CREATE TABLE Reviewed_At(

fid	            CHAR(7),
user_name    VARCHAR(20),
rid	            CHAR(7),
GM_link          VARCHAR(100),
date 	            DATE,

PRIMARY KEY(fid, user_name, GM_link),
FOREIGN KEY(fid) REFERENCES Foods,
FOREIGN KEY(user_name) REFERENCES Users,
FOREIGN KEY (GM_link)
REFERENCES Found_At(GM_link),
FOREIGN KEY(rid) REFERENCES Reviews
);




![image](https://user-images.githubusercontent.com/76651649/144515568-5be3aa6a-eedd-4cbc-9ff4-a70eedc56c33.png)
