import pymssql
from decouple import config


class ConnectionManager:

    def __init__(self):
        self.server_name = config('Server') + ".database.windows.net"
        self.db_name = config('DBName')
        self.user = config("UserID")
        self.password = config("Password")
        self.conn = None

    def create_connection(self):
        try:
            self.conn = pymssql.connect(
                                        server=self.server_name,
                                        user=self.user,
                                        password=self.password,
                                        database=self.db_name)
        except pymssql.Error as db_err:
            print("Database Programming Error in SQL connection processing! ")
            print(db_err)
            quit()
        return self.conn

    def close_connection(self):
        try:
            self.conn.close()
        except pymssql.Error as db_err:
            print("Database Programming Error in SQL connection processing! ")
            print(db_err)
            quit()
