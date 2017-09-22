--
-- PostgreSQL database init sequence for raf-eol-rt-data.
-- Aircraft users and databases are handled in the raf-ac-eolrtdata RPM.
--
-- This script is executed during rpm installation. To run manually, type
-- 'cat psql-init.sql | psql'
--

--
-- Create required users
--   - users without roles default to read only
--
CREATE USER ads;
ALTER ROLE ads superuser;

CREATE USER guest;
