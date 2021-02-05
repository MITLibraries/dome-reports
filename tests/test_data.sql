/*
   Foreign keys enforcement may not be turned on.
   The PRAGMA here does this.
*/

PRAGMA foreign_keys = ON;

BEGIN TRANSACTION;

INSERT INTO Community(uuid, name, short_name) VALUES('aaaaaaaa-e361-4685-a048-5f97bd08c466','Rotch Library Architecture','Rotch Library Architecture');
INSERT INTO Community(uuid, name, short_name) VALUES('bbbbbbbb-6115-4272-9487-429c1a45c93e','Digital Technology','Digital Technology');
INSERT INTO Community(uuid, name, short_name) VALUES('cccccccc-5a18-434a-a3ba-a001ef186b5f','MIT Libraries','MIT Libraries');
INSERT INTO Community(uuid, name, short_name) VALUES('dddddddd-ba85-4fdc-94c8-fd13048cbd1d','Lewis Music Library','Lewis Music Library');
INSERT INTO Community(uuid, name, short_name) VALUES('eeeeeeee-9843-4996-b590-8182f885c833','Visual Collections','Visual Collections');
INSERT INTO Community(uuid, name, short_name) VALUES('ffffffff-9843-4996-b590-8182f885c8ff','Dome Reports','Dome Reports');

INSERT INTO Collection(uuid, comm_uuid, name, short_name, reportable) VALUES('7b1d1752-9843-4996-b590-8182f885c833','eeeeeeee-9843-4996-b590-8182f885c833','Aga Khan Visual Archive','Aga Khan Visual Archive', 1);
INSERT INTO Collection(uuid, comm_uuid, name, short_name, reportable) VALUES('a5911166-e361-4685-a048-5f97bd08c466','aaaaaaaa-e361-4685-a048-5f97bd08c466','Perceptual Form of the City','Perceptual Form of the City', 1);
INSERT INTO Collection(uuid, comm_uuid, name, short_name, reportable) VALUES('e129658d-19f4-4a11-99f0-ce25b746bae5','eeeeeeee-9843-4996-b590-8182f885c833','Frankel Built Landscape Archive','Frankel Built Landscape Archive', 1);
INSERT INTO Collection(uuid, comm_uuid, name, short_name, reportable) VALUES('67d5e318-04fb-4840-954b-dd69c6c5ec2c','eeeeeeee-9843-4996-b590-8182f885c833','Research Photography by Jean Jackson','Research Photography by Jean Jackson', 1);
INSERT INTO Collection(uuid, comm_uuid, name, short_name, reportable) VALUES('62206c51-ba85-4fdc-94c8-fd13048cbd1d','dddddddd-ba85-4fdc-94c8-fd13048cbd1d','Inventions of Note','Inventions of Note', 1);
INSERT INTO Collection(uuid, comm_uuid, name, short_name, reportable) VALUES('ec2ce98d-6115-4272-9487-429c1a45c93e','bbbbbbbb-6115-4272-9487-429c1a45c93e','Project Whirlwind Reports','Project Whirlwind Reports', 1);
INSERT INTO Collection(uuid, comm_uuid, name, short_name, reportable) VALUES('929c8db8-d461-430c-9ce9-9356719e5c36','eeeeeeee-9843-4996-b590-8182f885c833','Reconstruction of Harvard Bridge','Reconstruction of Harvard Bridge', 1);
INSERT INTO Collection(uuid, comm_uuid, name, short_name, reportable) VALUES('a6f7a9c6-5a18-434a-a3ba-a001ef186b5f','cccccccc-5a18-434a-a3ba-a001ef186b5f','DSpace 7 Test Everything','DSpace 7 Test Everything', 1);
INSERT INTO Collection(uuid, comm_uuid, name, short_name, reportable) VALUES('b4f7a888-5a18-434a-83ba-a001ef678954','ffffffff-9843-4996-b590-8182f885c8ff', 'Monthly Collection Item Reports', 'Monthly Collection Items', 0);

INSERT INTO Monthly_Item_Count VALUES('7b1d1752-9843-4996-b590-8182f885c833',2021,1,33105);
INSERT INTO Monthly_Item_Count VALUES('7b1d1752-9843-4996-b590-8182f885c833',2021,2,33110);
INSERT INTO Monthly_Item_Count VALUES('7b1d1752-9843-4996-b590-8182f885c833',2021,3,33110);
INSERT INTO Monthly_Item_Count VALUES('7b1d1752-9843-4996-b590-8182f885c833',2021,4,33267);
INSERT INTO Monthly_Item_Count VALUES('a5911166-e361-4685-a048-5f97bd08c466',2021,1,2193);
INSERT INTO Monthly_Item_Count VALUES('a5911166-e361-4685-a048-5f97bd08c466',2021,2,2193);
INSERT INTO Monthly_Item_Count VALUES('a5911166-e361-4685-a048-5f97bd08c466',2021,3,2193);
INSERT INTO Monthly_Item_Count VALUES('a5911166-e361-4685-a048-5f97bd08c466',2021,4,2199);
INSERT INTO Monthly_Item_Count VALUES('e129658d-19f4-4a11-99f0-ce25b746bae5',2021,1,567);
INSERT INTO Monthly_Item_Count VALUES('e129658d-19f4-4a11-99f0-ce25b746bae5',2021,2,567);
INSERT INTO Monthly_Item_Count VALUES('e129658d-19f4-4a11-99f0-ce25b746bae5',2021,3,567);
INSERT INTO Monthly_Item_Count VALUES('e129658d-19f4-4a11-99f0-ce25b746bae5',2021,4,567);
INSERT INTO Monthly_Item_Count VALUES('67d5e318-04fb-4840-954b-dd69c6c5ec2c',2021,1,622);
INSERT INTO Monthly_Item_Count VALUES('67d5e318-04fb-4840-954b-dd69c6c5ec2c',2021,2,622);
INSERT INTO Monthly_Item_Count VALUES('67d5e318-04fb-4840-954b-dd69c6c5ec2c',2021,3,622);
INSERT INTO Monthly_Item_Count VALUES('67d5e318-04fb-4840-954b-dd69c6c5ec2c',2021,4,622);
INSERT INTO Monthly_Item_Count VALUES('62206c51-ba85-4fdc-94c8-fd13048cbd1d',2021,3,60);
INSERT INTO Monthly_Item_Count VALUES('62206c51-ba85-4fdc-94c8-fd13048cbd1d',2021,4,60);
INSERT INTO Monthly_Item_Count VALUES('ec2ce98d-6115-4272-9487-429c1a45c93e',2021,1,1719);
INSERT INTO Monthly_Item_Count VALUES('ec2ce98d-6115-4272-9487-429c1a45c93e',2021,2,1719);
INSERT INTO Monthly_Item_Count VALUES('ec2ce98d-6115-4272-9487-429c1a45c93e',2021,3,1719);
INSERT INTO Monthly_Item_Count VALUES('ec2ce98d-6115-4272-9487-429c1a45c93e',2021,4,1719);
INSERT INTO Monthly_Item_Count VALUES('929c8db8-d461-430c-9ce9-9356719e5c36',2021,1,15);
INSERT INTO Monthly_Item_Count VALUES('929c8db8-d461-430c-9ce9-9356719e5c36',2021,2,15);
INSERT INTO Monthly_Item_Count VALUES('929c8db8-d461-430c-9ce9-9356719e5c36',2021,3,15);
INSERT INTO Monthly_Item_Count VALUES('929c8db8-d461-430c-9ce9-9356719e5c36',2021,4,15);
INSERT INTO Monthly_Item_Count VALUES('a6f7a9c6-5a18-434a-a3ba-a001ef186b5f',2021,1,23);
INSERT INTO Monthly_Item_Count VALUES('a6f7a9c6-5a18-434a-a3ba-a001ef186b5f',2021,2,37);
INSERT INTO Monthly_Item_Count VALUES('a6f7a9c6-5a18-434a-a3ba-a001ef186b5f',2021,3,71);
INSERT INTO Monthly_Item_Count VALUES('a6f7a9c6-5a18-434a-a3ba-a001ef186b5f',2021,4,89);

INSERT INTO Monthly_Item_Count VALUES('b4f7a888-5a18-434a-83ba-a001ef678954',2021,1,1);
INSERT INTO Monthly_Item_Count VALUES('b4f7a888-5a18-434a-83ba-a001ef678954',2021,2,1);
INSERT INTO Monthly_Item_Count VALUES('b4f7a888-5a18-434a-83ba-a001ef678954',2021,3,1);
INSERT INTO Monthly_Item_Count VALUES('b4f7a888-5a18-434a-83ba-a001ef678954',2021,4,1);

COMMIT;


