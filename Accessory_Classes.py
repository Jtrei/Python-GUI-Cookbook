import sqlite3 as sql
import os, sys


class Database:
    def __init__(self, pathway):
        self.pathway: str = pathway

    # Account creation and login Methods - ACM
    def initialize(self):
        connection = sql.connect(self.pathway)
        cursor = connection.cursor()
        cursor.execute(
            f"""CREATE TABLE IF NOT EXISTS Login (
                        username text, 
                        password text, 
                        logged_in text, 
                        ID text)
                        """
        )
        connection.commit()
        connection.close()

    # ACM
    def add_new_account(self, username, password):
        def check_return_ID():  # Used to calculate unique ID code per account
            connection = sql.connect(self.pathway)
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM Login")
            result = cursor.fetchall()
            connection.close()
            if result == []:
                return "1"
            else:
                return str(((result[0])[0]) + 1)

        user_id: str = check_return_ID()
        logged_in: str = "0"
        connection = sql.connect(self.pathway)
        cursor = connection.cursor()
        cursor.execute(
            f"INSERT INTO Login(username, password, logged_in, ID) VALUES (?,?,?,?);",
            (username, password, logged_in, user_id),
        )
        connection.commit()
        connection.close()

    # ACM
    def create_new_recipe_table(self, username):
        connection = sql.connect(self.pathway)
        cursor = connection.cursor()
        cursor.execute(
            f"""CREATE TABLE IF NOT EXISTS {username}_Recipes ( 
                       rec_ID integer,
                       website_name text, 
                       title text, 
                       cuisine text, 
                       cook_time text,
                       servings text, 
                       serving_size text, 
                       ingredients text, 
                       directions text,
                       nutrition_info text, 
                       notes text, 
                       picture blob)"""
        )
        connection.commit()
        connection.close()

    def query_on_startup(self):
        try:
            connection = sql.connect(self.pathway)
            cursor = connection.cursor()
            cursor.execute(f"SELECT * FROM Login")
            table = cursor.fetchall()
            for entry in table:
                if entry[2] == "1":
                    username, password, keep_logged = (entry[0], entry[1], entry[2])
            connection.commit()
            connection.close()
            if keep_logged == "1":
                return username, password, keep_logged
            else:
                return "", "", "0"
        except:
            return "", "", "0"

    def login(self, username, password):
        connection = sql.connect(self.pathway)
        cursor = connection.cursor()
        cursor.execute(f"SELECT * FROM Login")
        table = cursor.fetchall()
        connection.close()
        for entry in table:
            if username == entry[0] and password == entry[1]:
                username_db, password_db = entry[0], entry[1]
                return username_db, password_db

    def update_logged_in(self, username):
        connection = sql.connect(self.pathway)
        cursor = connection.cursor()
        cursor.execute(f"SELECT * FROM Login")
        table = cursor.fetchall()
        for entry in table:
            user = entry[0]
            if user == username:
                logged = "1"
            else:
                logged = "0"
            query: str = f""" UPDATE Login
                               SET logged_in = '{logged}'
                               WHERE username = '{user}'"""
            cursor.execute(query)
        connection.commit()
        cursor.execute(f"SELECT * FROM Login")
        check_for_table = cursor.fetchall()
        connection.close()

    def write_recipe_to_database(self, recipe, username):
        def rec_ID_return(username):
            connection = sql.connect(self.pathway)
            cursor = connection.cursor()
            cursor.execute(f"SELECT * FROM {username}_Recipes")
            recipe_list = cursor.fetchall()
            id_num = len(recipe_list) + 1
            connection.commit()
            connection.close()
            return id_num

        id_num = rec_ID_return(username)
        connection = sql.connect(self.pathway)
        cursor = connection.cursor()
        cursor.execute(
            f"""INSERT INTO {username}_Recipes(rec_ID, website_name, title, cuisine, cook_time, servings, serving_size, ingredients, directions, nutrition_info, notes, picture) 
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?);""",
            (
                id_num,
                recipe.website_name,
                recipe.title,
                recipe.cuisine,
                recipe.cook_time,
                recipe.servings,
                recipe.serving_size,
                recipe.ingredients,
                recipe.directions,
                recipe.nutrition_info,
                recipe.notes,
                recipe.picture,
            ),
        )
        connection.commit()
        connection.close()

    def return_photo_list(self):
        photo_list = []
        users = []
        connection = sql.connect(self.pathway)
        cursor = connection.cursor()
        cursor.execute(f"SELECT * FROM Login")
        table_log = cursor.fetchall()
        for entry in table_log:
            cursor.execute(f"SELECT * FROM {entry[0]}_Recipes")
            table_users = cursor.fetchall()
            for user in table_users:
                try:
                    photo_list.append(user[-1])
                except IndexError:
                    pass
                    # print(f'user {entry[0]} does not have any photos')
        connection.close()
        return photo_list


class Recipe:
    def __init__(
        self,
        website_name,
        title,
        cuisine,
        cook_time,
        servings,
        serving_size,
        ingredients,
        directions,
        nutrition_info,
        notes,
        picture,
    ):
        self.website_name = website_name
        self.title = title
        self.cuisine = cuisine
        self.cook_time = cook_time
        self.servings = servings
        self.serving_size = serving_size
        self.ingredients = ingredients
        self.directions = directions
        self.nutrition_info = nutrition_info
        self.notes = notes
        self.picture = picture

    def __repr__(self):
        return f"""
        'website':{self.website_name}, 
        'title':{self.title}, 
        'cuisine':{self.cuisine}, 
        'cook_time':{self.cook_time}, 
        'servings':{self.servings}, 
        'serving_size':{self.serving_size}, 
        'ingredients':{self.ingredients}, 
        'directions':{self.directions},
        'nutrition_info':{self.nutrition_info}, 
        'Notes':{self.notes},
        'Picture':{self.picture}
        """

    def file_writer(self, file_name, *arg, **kwarg):
        with open(file_name, "w") as RecipeWriter:
            RecipeWriter.write(
                f""" Website title: {self.website_name}
                                    Recipe title: {self.title}

                                    Cuisine type: {self.cuisine}

                                    Servings: {self.servings}
                                    Serving Size: {self.serving_size}
                                    Cook time: {self.serving_size} minutes
                                    Nutrition info: 
                                    {self.nutrition_info}

                                    Ingredients: 
                                    {self.ingredients}

                                    Directions: 
                                    {self.directions}
                                    
                                    Notes: 
                                    {self.Notes}
                                                """
            )
