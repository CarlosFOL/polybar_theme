import json
import os
import pandas as pd
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
        Open/Close connection to the WeatherData DB

        Args:
            close: bool
                Indicate whether or not the connection needs to be closed.
        """
        if close:
            self.conn.close()
            self.conn = None
        else:
            self.conn = self.conn = sqlite3.connect("WeatherData")

    def _which_query(self, keys: tuple):
        """Retrieve a specific query.

        Specify which SQL query you want to retrieve.

        Args:
            keys: tuple
                Keys to navigate into the query JSON file.
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
        return os.path.exists(self.path + "WeatherData")

    def execute_query(self, sql_keys: tuple, parameters: tuple = None, read: bool = False):
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
        query = self._which_query(keys=sql_keys)

        if self.conn is None:
            self._manage_conn()

        cursor = self.conn.cursor()

        if parameters is None:
            try:
                cursor.execute(query)
            except sqlite3.ProgrammingError: # In case of Multiple Row Insertion
                cursor.executemany(query)
        else:
            try:
                cursor.execute(query, parameters)
            except sqlite3.ProgrammingError:
                cursor.executemany(query, parameters)

        if read:
            results = cursor.fetchall()
            return results if results else []
        else:
            # For INSERT, UPDATE, DELETE operations
            self.conn.commit()
            return cursor.rowcount  # Number of affected rows

    def create_db(self, force:bool=False):
        """
        Create the WeatherData database schema by executing
        the file tables.sql.

        Args:
            force: bool
                To force create the database from scratch.
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

            self._manage_conn(close=True)
        else:
            print("WeatherData DB already exists.")


    def insert_wobservations(self, data: pd.DataFrame):
        """
        Special method to only insert the new data into the
        WeatherObservation table when either the end date is expired, the location has changed, or the app was initialized for the first time.
        """
        self._manage_conn()
        data.to_sql("WeatherObservation", con=self.conn, if_exists="replace")
        self._manage_conn(close=True)
