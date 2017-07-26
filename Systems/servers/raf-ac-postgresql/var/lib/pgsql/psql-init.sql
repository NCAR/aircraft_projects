--
-- PostgreSQL database init sequence. Use this for both eol-rt-data and 
-- installation on aircraft so keep it generic. platform-specific users
-- and databases are handled in platform-specific RPMs. See 
-- raf-ac-eolrtdata RPM.
--
-- This script is executed during rpm installation. To run manually, type
-- 'cat psql-init.sql | psql'
--

--
-- Create required users
--   - users without roles default to read only
--
CREATE USER ads with LOGIN PASSWORD 'ads';

CREATE USER nimbus with LOGIN PASSWORD 'nimbus';
ALTER ROLE nimbus superuser;

