# # db.py
# import mysql.connector
# from mysql.connector import Error
# from config import Config

# def get_db_connection():
#     # Thiết lập kết nối đến cơ sở dữ liệu MySQL
#     db = mysql.connector.connect(
#         host=Config.MYSQL_HOST,
#         user=Config.MYSQL_USER,
#         password=Config.MYSQL_PASSWORD,
#         database=Config.MYSQL_DB
#     )
#     return db

# def check_db_connection():
#     try:
#         db = get_db_connection()
#         if db.is_connected():
#             print("Kết nối đến MySQL thành công")
#             db.close()
#         else:
#             print("Kết nối đến MySQL thất bại")
#     except Error as e:
#         print(f"Lỗi khi kết nối đến MySQL: {e}")


import mysql.connector
from mysql.connector import Error
from config import Config

def get_db_connection():
    try:
        # Establish a connection to the MySQL database
        db = mysql.connector.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DB
        )
        return db
    except Error as e:
        # If there's an error, raise an exception or return the error message
        raise Exception(f"Failed to connect to MySQL: {e}")

def check_db_connection():
    try:
        db = get_db_connection()
        if db.is_connected():
            print("Connected to MySQL successfully")
            db.close()
        else:
            print("Failed to connect to MySQL")
    except Exception as e:
        print(f"Error checking MySQL connection: {e}")
