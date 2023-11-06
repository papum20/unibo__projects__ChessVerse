from backend.db_connection import cursor, conn
import random

def is_nickname_in_database(nickname):
   cursor.execute("SELECT * FROM Guest WHERE Username=%s", (nickname,))
   result = cursor.fetchone()
   
   if(result is not None):
     return True
   
   return False

def generate_random_nickname():
    while True:
        random_number = random.randint(1, 1000000000)
        nickname = f'Guest-{random_number}'
        
        if (is_nickname_in_database(nickname) == False):
            return nickname


guest_nickname = ''
 
def add_guest():
   global guest_nickname 
   guest_nickname = generate_random_nickname()
   insert_query = "INSERT INTO Guest (Username) VALUES (%s)"
   cursor.execute(insert_query, (guest_nickname,))
   conn.commit()


def get_guest_name():
    return guest_nickname
