--
-- PostgreSQL database init sequence for eol-rt-data. This is executed 
-- during rpm installation. To run manually, type 
-- 'cat psql-init.sql | psql'
--
-- Create required users
--
CREATE USER ads with LOGIN PASSWORD 'ads';
CREATE USER janine with LOGIN PASSWORD 'janine';
CREATE USER nimbus with LOGIN PASSWORD 'nimbus';
ALTER ROLE nimbus superuser;
