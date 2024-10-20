import sqlite3

class SQLiteHandler:
    _instances = {}

    def __new__(cls, db_name):
        """Ensure only one instance exists per database file."""
        if db_name not in cls._instances:
            cls._instances[db_name] = super(SQLiteHandler, cls).__new__(cls)
            cls._instances[db_name]._initialize(db_name)
        return cls._instances[db_name]

    def _initialize(self, db_name):
        """Private method to initialize the database connection."""
        self.db_name = db_name
        self._connect()

    def _connect(self):
        """Establish a connection to the SQLite database (only once per file)."""
        if not hasattr(self, '_connection'):
            try:
                self._connection = sqlite3.connect(self.db_name)
                print(f"Connected to {self.db_name}")
            except sqlite3.Error as e:
                print(f"Error connecting to database: {e}")
        else:
            print(f"Already connected to {self.db_name}")

    def create_table(self, table_name, fields):
        """
        Create a table with the given name and fields.
        
        :param table_name: Name of the table
        :param fields: A dictionary where the key is the field name and the value is the data type (e.g., 'TEXT', 'INTEGER')
        """
        try:
            cursor = self._connection.cursor()
            columns = ', '.join([f"{field} {dtype}" for field, dtype in fields.items()])
            cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({columns})")
            self._connection.commit()
            print(f"Table {table_name} created successfully.")
        except sqlite3.Error as e:
            print(f"Error creating table: {e}")

    def insert_row(self, table_name, data):
        """
        Insert a row into the specified table.
        
        :param table_name: Name of the table
        :param data: A dictionary where the key is the field name and the value is the data to insert
        """
        try:
            cursor = self._connection.cursor()
            fields = ', '.join(data.keys())
            placeholders = ', '.join('?' for _ in data.values())
            values = tuple(data.values())
            cursor.execute(f"INSERT INTO {table_name} ({fields}) VALUES ({placeholders})", values)
            self._connection.commit()
            print(f"Inserted row into {table_name}.")
        except sqlite3.Error as e:
            print(f"Error inserting row: {e}")

    def get_rows_by_field(self, table_name, field, value):
        """
        Get rows from the specified table where the field matches the value.
        
        :param table_name: Name of the table
        :param field: Field name to filter by
        :param value: Value to match
        :return: List of dictionaries where each dict represents a row (field names are keys).
        """
        try:
            cursor = self._connection.cursor()
            cursor.execute(f"SELECT * FROM {table_name} WHERE {field} = ?", (value,))
            rows = cursor.fetchall()

            # Fetch column names
            column_names = [description[0] for description in cursor.description]

            # Convert rows to list of dictionaries
            result = [dict(zip(column_names, row)) for row in rows]

            return result
        except sqlite3.Error as e:
            print(f"Error fetching rows: {e}")
            return []
    
    def get_all_rows(self, table_name):
        """
        Get all rows from the specified table.
        
        :param table_name: Name of the table
        :return: List of dictionaries where each dict represents a row (field names are keys).
        """
        try:
            cursor = self._connection.cursor()
            cursor.execute(f"SELECT * FROM {table_name}")
            rows = cursor.fetchall()

            # Fetch column names
            column_names = [description[0] for description in cursor.description]

            # Convert rows to list of dictionaries
            result = [dict(zip(column_names, row)) for row in rows]

            return result
        except sqlite3.Error as e:
            print(f"Error fetching rows: {e}")
            return []



    def close(self):
        """Close the database connection."""
        if hasattr(self, '_connection'):
            self._connection.close()
            del self._connection
            print(f"Connection to {self.db_name} closed.")



# db1 = SQLiteHandler('ecommerce.db')

# fields = {
#     'id': 'INTEGER PRIMARY KEY AUTOINCREMENT',
#     'name': 'TEXT',
#     'repo': 'TEXT',
#     'production_branch': 'TEXT',
#     'development_branch': 'TEXT'
# }

# db1.create_table('projects',fields)

# row = {'name': 'Project 1', 'repo': 'project1', 'production_branch': 'main', 'development_branch': 'dev'}
# row2 = {'name': 'Project 2', 'repo': 'project2', 'production_branch': 'master', 'development_branch': 'develop'}
# db1.insert_row('projects', row)
# db1.insert_row('projects', row2)

# row = db1.get_rows_by_field('projects', 'name', 'Project 1')
# print(row)
# print("************************************************************")
# print(db1.get_all_rows('projects'))
# db1.close()