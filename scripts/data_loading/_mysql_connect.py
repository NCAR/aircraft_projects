#!/usr/bin/env python
import os
import pymysql # type: ignore

class mysqlConnect:
    """
    This is the connect function within the class. Given "column", "table"
    inputs, it will pull the selected information and write the list into
    the output file "write_name"
    """

    def __init__(self, group):
        # Read connection info from a .my.cnf specified using the environment
        # variable DMG_MYCNF_PATH, or default to file in user's home dir.
        self.mycnf = os.getenv('DMG_MYCNF_PATH') \
                if os.getenv('DMG_MYCNF_PATH') else "~/.my.cnf"

        self.group = group  # make global

    def connectCODIAC(self, column, table, write_name, zith9dict):
        # Connect to database specified under [perl] group in .my.cnf file
        zith_cnx = pymysql.connect(database='zith9',
                                   read_default_file=self.mycnf,
                                   read_default_group=self.group)
        cursor = zith_cnx.cursor()
        # Query to get column names from the information schema
        column_query = ("SELECT COLUMN_NAME FROM information_schema.columns "
                        "WHERE table_schema = 'zith9' AND table_name = %s")
        cursor.execute(column_query, (table,))
         # Fetch and print column names
        """ columns = cursor.fetchall()
        print("Columns in table '{}':".format(table))
        for col in columns:
            print(col[0]) """
        # Variables used for special WHERE cases.
        where_pn = "WHERE active_editor=1 and person_name!='NULL'"
        # where_pna = "WHERE person_name!='NULL'"
        where_ona = "WHERE organization_name!='NULL'"
        where_sn = "WHERE short_name!='NULL'"

        # Query database with inputs and special WHERE variables when needed.
        if column == "person_name" and table == "contact":
            if write_name == "codiac_contact_id_active":
                query = ("SELECT id, %s FROM %s %s" %
                         (column, table, where_pn))
            elif write_name == "codiac_contact_id_all":
                query = ("SELECT id, IFNULL(%s, organization_name) %s \
                         FROM %s %s" % (column, column, table, where_ona))
        elif column == "short_name" and table == "format":
            query = ("SELECT id, %s FROM %s %s" % (column, table, where_sn))
        else:
            # Default query
            query = ("SELECT id, %s FROM %s" % (column, table))

        cursor.execute(query)

        # Create a list record and fill with database information
        record = []
        for (id, column) in cursor:
            try:
                column = column.replace(":", "")
            except AttributeError:
                pass
            record.append((id, column))

        # Sort list by id number
        record.sort()

        # Write list to zith9 dictionary
        for (id, column) in record:
            zith9dict[write_name][id] = column

        # Close out
        cursor.close()
        zith_cnx.close()

    def connectDTS(self, column, table, write_name, zith9dict):
        # Connect to database specified under [dts] group in .my.cnf file

        # If already read in this table, return
        if zith9dict[write_name]:  # dictionary for write_name not empty
            return()

        dts_cnx = pymysql.connect(database='dmg_dts',
                                read_default_file=self.mycnf,
                                read_default_group=self.group)
        cursor = dts_cnx.cursor()

        where_ae = "WHERE active_editor=1"

        if column == "contact_short_name":
            if write_name == "dts_contact_id_active":
                query = ("SELECT contact_id, %s FROM %s %s" %
                         (column, table, where_ae))
            elif write_name == "dts_contact_id_all":
                query = ("SELECT contact_id, %s FROM %s" % (column, table))

        elif column == "name":
            query = ("SELECT status_id, %s FROM %s" % (column, table))

        cursor.execute(query)

        record = []
        for (id, column) in cursor:
            column = column.replace(":", "")
            record.append((id, column))

        # Sort list by id number
        record.sort()

        # Write list to zith9 dictionary
        for (id, column) in record:
            zith9dict[write_name][id] = column

        # Close out
        cursor.close()
        dts_cnx.close()
