import random
import mysql.connector

con = mysql.connector.connect(
    host="localhost",
    user="root",
    password="0000",
    database="leafy"
)
cursor = con.cursor()

def insert_vase():
    uuid = f"LEAFY-{random.randint(0, 999999):06d}"
    cursor.execute('INSERT INTO vases (id) VALUES (%s)', (uuid,))
    con.commit()
    return uuid

def insert_user(user_id, user_name):
    cursor.execute('INSERT INTO users (telegramId, name) VALUES (%s, %s)', (user_id, user_name))
    con.commit()
    return user_id

def check_if_user_exist(user_id,):
    cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
    result = cursor.fetchone()
    if result:
        print("User already exists")
        return True
    else:
        print("User does not exist")
        return False
