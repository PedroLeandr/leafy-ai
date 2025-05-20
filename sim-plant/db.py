import mysql.connector

con = mysql.connector.connect(
    host="localhost",
    user="root",
    password="0000",
    database="Leafy"
)

cursor = con.cursor()
