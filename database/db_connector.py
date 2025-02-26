import pymysql
pymysql.install_as_MySQLdb()
import MySQLdb
import database.db_credentials as db_credentials

def connect_to_database():
    """Creates a connection to the database."""
    db_connection = MySQLdb.connect(
        host=db_credentials.host,
        user=db_credentials.user,
        passwd=db_credentials.passwd,
        db=db_credentials.db,
        cursorclass=MySQLdb.cursors.DictCursor
    )
    return db_connection

def execute_query(db_connection, query, data=None):
    """Executes a query on the database and returns results."""
    cursor = db_connection.cursor()
    cursor.execute(query, data) if data else cursor.execute(query)
    db_connection.commit()
    return cursor
