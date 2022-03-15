import mysql.connector
import time
from api.logger import logger

mydb = None

def connect_database():
  time.sleep(5)

  mydb = mysql.connector.connect(
    host='db',
    user='root',
    password='password',
    database="888spectate"
  )
  return mydb

def set_database(db):
  global mydb
  mydb = db

def get_database():
  return mydb

def verify_table_exists(table_name):
    show_tables_cursor = mydb.cursor()
    show_tables_cursor.execute("SHOW TABLES")
    tables = [table_name[0] for table_name in show_tables_cursor]
    return table_name in tables
