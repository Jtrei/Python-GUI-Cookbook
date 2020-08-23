import sqlite3, os, sys

class Database:
    def __init__(self, pathway): 
        self.pathway: str = pathway

    # Account creation and login Methods - ACM
    def initialize(self):
        connection = sqlite3.connect(self.pathway)
        cursor = connection.cursor()
        cursor.execute(f'''CREATE TABLE IF NOT EXISTS Login (
                        username text, 
                        password text, 
                        logged_in text, 
                        ID text,
                        recipe_pathway text)
                        ''')
        connection.commit()
        connection.close()

    # ACM
    def add_new_account(self, username, password, recipe_pathway): # Logger.add_new_account(username, password, recipe_pathway)
        user_id: str = self.check_return_ID()
        logged_in: str = '0'
        connection = sqlite3.connect(self.pathway)
        cursor = connection.cursor()
        cursor.execute(f"INSERT INTO Login VALUES ('{username}', '{password}', '{logged_in}', '{user_id}', '{recipe_pathway}')")
        connection.commit()
        connection.close()

        # ACM
        def check_return_ID(self): # Used to calculate unique ID code per account
            connection = sqlite3.connect(self.pathway)
            cursor = connection.cursor()
            cursor.execute("SELECT COUNT (*) FROM Login")  
            result = cursor.fetchall()
            connection.close()
            return str(((result[0])[0])+1)

    # ACM
    def create_new_recipe_database(self, username):
        connection = sqlite3.connect(self.pathway)
        cursor = connection.cursor()
        cursor.execute(f'''CREATE TABLE IF NOT EXISTS {username}_Recipes ( 
                       rec_ID integer,
                       website_name text, 
                       title text, 
                       cuisine text, 
                       cook_time integer,
                       servings text, 
                       serving_size integer, 
                       ingredients text, 
                       directions text,
                       nutrition_info text, 
                       notes text, 
                       picture blob)''')
        connection.commit()
        connection.close()

    def query_on_startup(self):
        try:
            connection = sqlite3.connect(self.pathway)
            cursor = connection.cursor()
            cursor.execute(f"SELECT * FROM Login")
            table = cursor.fetchall()
            for entry in table:
                print(entry)
                if entry[2] == '1':
                    username, password, keep_logged = (entry[0], entry[1], entry[2])
            connection.commit()
            connection.close()
            if keep_logged == "1":
                return username, password, keep_logged 
            else:
                return '','','0'
        except:
            return '', '', '0'

    def login(self, username, password):
        connection = sqlite3.connect(self.pathway)
        cursor = connection.cursor()
        cursor.execute(f"SELECT * FROM Login")
        table = cursor.fetchall()
        connection.close()
        for entry in table:
            if username == entry[0] and password == entry[1]:
                username_db, password_db = entry[0], entry[1]
                return username_db, password_db
        return username, password

    def update_logged_in(self, username):
        connection = sqlite3.connect(self.pathway)
        cursor = connection.cursor()
        cursor.execute(f"SELECT * FROM Login")
        table = cursor.fetchall()
        for entry in table:
            user = entry[0]
            if user == username:
                logged = '1'
            else:
                logged = '0'
            query: str =  f""" UPDATE Login
                               SET logged_in = '{logged}'
                               WHERE username = '{user}'"""
            cursor.execute(query)
        connection.commit()
        cursor.execute(f"SELECT * FROM Login")
        check_for_table = cursor.fetchall()
        print(check_for_table)
        connection.close()

    def rec_ID_return(self):
        connection = sqlite3.connect(self.database_file)
        cursor = connection.cursor()
        cursor.execute(f"SELECT * FROM {self.username}_Recipes")
        recipe_list = cursor.fetchone()
        print(recipe_list)
        connection.commit()
        connection.close()
        return "foo"

    def add_recipe_to_database(self):
        pass
    