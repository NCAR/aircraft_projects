--
-- PostgreSQL database init sequence for postgres on the aircraft.
-- Ground users and databases are handled in the raf-eol-rt-data RPM.
--
-- This script is executed during rpm installation. To run manually, type
-- 'cat psql-init.sql | psql'
--

--
-- Create required users
--   - users without roles default to read only
--
CREATE USER ads with LOGIN PASSWORD 'snoitarbilac';
ALTER ROLE ads superuser;

