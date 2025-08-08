#!/usr/bin/env python3

# Create the database and the tables within in.
import json
import os
import sqlite3

class WeatherDB:
    """
    Data Access Object for managing the WeatherData database.

    It can verify whether the database already exists; if not, it can
    create it. Also, it provides a method to add records to the table
    WeatherObservations, and to empty this table.

    Methods:
        exist() -> bool:
            Check if the database was created.
        create_db():
            Create the WeatherData database.
        add_WeatherObservations():
            Insert the data into the table WeatherObservations.
    """

    def __init__(self):
        self.path = "" if os.path.exists("db") else "../"
        with open(self.path + "db/queries.json", "r") as f:
            queries = f.read()
        self.__queries = json.loads(queries) # SQL statements to use across the methods.

        self.conn = None # DB Connection

    @property
    def queries(self):
        return self.__queries

    def _manage_conn(self, close:bool=False):
        """
        Open connection to the WeatherData DB
        """
        if close:
            self.conn.close()
            self.conn = None
        else:
            self.conn = self.conn = sqlite3.connect("WeatherData")

    def _which_query(self, keys: tuple):
        """Retrieve a specific query.

        Specify which SQL query you want to retrieve.
        """
        # To work with a nested dictionary
        query = self.queries.get(keys[0])
        for k in keys[1:]:
            query = query.get(k)
        return query

    def exists(self) -> bool:
        """
        Check if the WeatherData database was created.
        """
        return os.path.exists(self.path + "db/WeatherData")

    def _execute_query(self, sql: str, parameters: tuple = None, read: bool = True):
        """
        Execute a sql query with its corresponding parameters.

        Args:
            sql: str
                SQL query.
            parameters: tuple
                Parameters to pass to query.
            read: bool
                Indicate wheter it's a read operation.
        """
        if self.conn is None:
            self._manage_conn()

        cursor = self.conn.cursor()

        if parameters is None:
            try:
                cursor.execute(sql)
            except sqlite3.ProgrammingError: # In case of Multiple Row Insertion
                cursor.executemany(sql)
        else:
            try:
                cursor.execute(sql, parameters)
            except sqlite3.ProgrammingError:
                cursor.executemany(sql, parameters)

        if read:
            results = cursor.fetchall()
            return results if results else []
        else:
            # For INSERT, UPDATE, DELETE operations
            self.conn.commit()
            return cursor.rowcount  # Number of affected rows

    def _fill_wvariables(self):
        """
        Insert the values of the table WeatherVariables by executing
        the file wvariables.sql.
        """
        wvariables = (('temperature', 'degC'),
                     ('wind', 'kmh_deg'),
                     ('precipitation', 'lm2'))
        sql = self._which_query(keys=("WVariable", "Fill"))
        self._execute_query(sql=sql, parameters=wvariables, read=False)

    def create_db(self, force:bool=False):
        """
        Create the WeatherData database schema by executing
        the file tables.sql.
        """
        if not self.exists() or (self.exists() and force):
            self._manage_conn() # Open connection

            if not os.path.exists(self.path + "db/tables.sql"):
                raise FileNotFoundError("The tables.sql file was not found. \
                                        Check to see if this file was deleted or if its path changed.")

            cursor = self.conn.cursor()
            with open(self.path + "db/tables.sql", "r") as f:
                tables = f.read()

            cursor.executescript(tables)
            self.conn.commit()

            # Fill the table WeatherVariable
            self._fill_wvariables()

            self._manage_conn(close=True)
        else:
            print("WeatherData DB already exists.")


    def add_WeatherObservations(self):
        pass
