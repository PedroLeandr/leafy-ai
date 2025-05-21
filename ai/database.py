import random
import mysql.connector

con = mysql.connector.connect(
    host="localhost",
    user="root",
    password="0000",
    database="leafy"
)
cursor = con.cursor()

user_name = ""


def check_if_user_exist(user_id,):
    cursor.execute('SELECT * FROM users WHERE telegramId = %s', (user_id,))

    result = cursor.fetchone()

    if result:
        print("User already exists:", result[2])
        return True
    else:
        print("User does not exist")
        return False
    
    user_id = result[1]
    user_name = result[2]

def insert_user(user_id, user_name):
    cursor.execute('INSERT INTO users (telegramId, name) VALUES (%s, %s)', (user_id, user_name))
    con.commit()
    return user_id

def insert_vase():
    uuid = f"LEAFY-{random.randint(0, 999999):06d}"
    cursor.execute('INSERT INTO vases (id) VALUES (%s)', (uuid,))
    con.commit()
    return uuid

def check_empty_vases():
    cursor.execute('SELECT * FROM vases WHERE plantId IS NULL')
    result = cursor.fetchall()
    return result

def check_busy_vases():
    cursor.execute('SELECT * FROM vases WHERE plantId IS NOT NULL')
    result = cursor.fetchall()
    return result

def check_vase_owner(vase_id):
    cursor.execute('SELECT * FROM vases_users WHERE vaseId = %s', (vase_id,))
    result = cursor.fetchone()
    if result:
        return result[1]
    else:
        return None
    
def check_owner_vases(user_id):
    cursor.execute('SELECT * FROM vases_users WHERE userId = %s', (user_id,))
    result = cursor.fetchone()
    if result:
        return result[1]
    else:
        return None
    
def insert_vase_owner(vase_id, user_id):
    cursor.execute('INSERT INTO vases_users (vaseId, userId) VALUES (%s, %s)', (vase_id, user_id))
    con.commit()
    return vase_id


print(check_empty_vases())
print(check_busy_vases())
print(check_vase_owner("LEAFY-119540"))
print(insert_vase_owner("LEAFY-119540", 1))
