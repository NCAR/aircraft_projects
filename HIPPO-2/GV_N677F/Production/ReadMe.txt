The flights are processed with some changes applied individually.
FlightGroups is used to remove variables that are not needed to be output into
the production files. Flight_rf01 was not using any special changes, so it is used
as the primary configuration for all other flights.

RF03 and others that have Flight_rfxx present are using changed dependencies, usually
due to the gaps in TAS or ADIFR.
