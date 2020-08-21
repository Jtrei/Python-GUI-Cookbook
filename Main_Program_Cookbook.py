import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
from WebsiteRecipeExtractor import *
import sys
import configparser
from PIL import Image, ImageTk
from Recipe_Classes import *
from Database_Class import *
from Error_Handling import *

# GLOBALS: Directories
folder_path_to_data_folder = os.path.join(os.getcwd(), 'Data')                                               # .\Data
folder_path_to_configuration_directory = os.path.join(folder_path_to_data_folder, 'Configuration')           # .\Data\Configuration
folder_path_to_database: str = os.path.join(folder_path_to_data_folder, 'Database')                          # .\Data\Database
# Files
file_path_to_database: str = os.path.join(folder_path_to_database, 'Global.db')                              # .\Data\Database\Global.db
# Data Structures
current_user_info: dict = {'username':'','recipe_folder_file_path':'','recipe_database_file_path':'','recipe_picture_folder_file_path':''}


# --- Startup Functions --- Create directories, files, and database if not already existing
def startup_settings(): 
    if os.path.exists(os.path.join(folder_path_to_configuration_directory, 'Configuration.ini')):
        pass
    elif not os.path.exists(folder_path_to_data_folder):
        os.mkdir(folder_path_to_data_folder)
        os.mkdir(folder_path_to_configuration_directory)
        os.mkdir(folder_path_to_database)
        global_database = Database(file_path_to_database)
        global_database.initialize()

        os.chdir(folder_path_to_configuration_directory)

        config = configparser.ConfigParser()
        config['Folder Paths'] = {
                                    'Data': folder_path_to_data_folder, 
                                    'Configuration': folder_path_to_configuration_directory,
                                    'Database': folder_path_to_database
                                    }
        config['File Paths'] = {
                                    'Database': file_path_to_database
                                    }
        with open('Configuration.ini', 'w') as ConfigFile:
            config.write(ConfigFile) 

# --- First GUI Interface ---  
# Startup app where a user may login or create an account
class StartupGUI(tk.Tk): 
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        container = tk.Frame(self)
        container.pack(side="top", fill='both', expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        main_menu_bar = tk.Menu(container)
        tk.Tk.config(self, menu=main_menu_bar)

        submenus = (
            ('Add Recipe Manually', 'Add Recipe from Website', 'Browse Recipes', 'Import Recipes (from file)', 'Export Recipes (to file)'),  # submenus[0][0-4]
            ('Edit Recipe', 'Edit Settings', 'Edit View'))  # submenus[1][0-2]
        recipe_sub_menu = tk.Menu(main_menu_bar, tearoff=0)
        recipe_sub_menu.add_command(label=submenus[0][0], command=lambda: self.menu_check(Manual_Recipe_Adder))
        recipe_sub_menu.add_command(label=submenus[0][1], command=lambda: self.menu_check(OnlineRecipeTool))
        recipe_sub_menu.add_separator()
        recipe_sub_menu.add_command(label=submenus[0][2], command=lambda: self.menu_check(RecipeList))
        recipe_sub_menu.add_separator()
        recipe_sub_menu.add_command(label=submenus[0][3])
        recipe_sub_menu.add_command(label=submenus[0][4])
        edit_sub_menu = tk.Menu(main_menu_bar, tearoff=0)
        edit_sub_menu.add_command(label=submenus[1][0])
        edit_sub_menu.add_separator()
        edit_sub_menu.add_command(label=submenus[1][1])
        edit_sub_menu.add_command(label=submenus[1][2])

        menus = ('Recipes', 'Edit')
        main_menu_bar.add_cascade(label=menus[0], menu=recipe_sub_menu)
        main_menu_bar.add_cascade(label=menus[1], menu=edit_sub_menu)

        self.frames = {}
        # First GUI contains Login and Account Creation Frames
        for F in (LoginPage, AccountCreationPage, Main_Page, Recipe_Browser, OnlineRecipeTool, Manual_Recipe_Adder): 
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky='nsew')


        self.show_frame(LoginPage)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()
        #            frame.winfo_toplevel().geometry("")

    def menu_check(self, page):
        if current_user_info['username'] != '':
            self.show_frame(page)

class LoginPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        username_label = tk.Label(self, text='Username: ')
        username_label.grid(row=0, column=0, pady=(10, 0), padx=10, sticky='w')
        self.username_entry = tk.Entry(self, width=30)
        self.username_entry.grid(row=0, column=1, padx=10)
        self.username_entry.focus()

        password_label = tk.Label(self, text='Password: ')
        password_label.grid(row=1, column=0, padx=10, sticky='w')
        self.password_entry = tk.Entry(self, show='*', width=30)
        self.password_entry.grid(row=1, column=1, padx=10)

        var1 = tk.IntVar()
        self.keep_logged_ckb = tk.Checkbutton(self, text='Keep signed in?', variable=var1, onvalue=1, offvalue=0)
        self.keep_logged_ckb.grid(row=2, column=0, columnspan=2)

        enter_login = tk.Button(self, text="Submit", command=lambda:
        self.login_function(self.username_entry.get(), self.password_entry.get(), var1.get(), parent))
        enter_login.grid(row=3, column=0, columnspan=2, pady=2)

        create_account = tk.Button(self, text='Create Account', command=lambda: controller.show_frame(AccountCreationPage))
        create_account.grid(row=4, column=0, columnspan=2, pady=2)

        # Label holder for login error handling responses
        self.log_response = tk.Label(self, text='foo') 

        self.if_stay_logged_skip_screen()
    
    # Searches login database to see if previous user wanted to remain logged in. The .keep_logged_in method below
    # ensures that only one user will have a "1" value in the database column for keep_logged. If so, the fields will
    # become pre-populated.
    def if_stay_logged_skip_screen(self): 
        last_use_db = Database(file_path_to_database)
        username, password, keep_logged = last_use_db.query_on_startup()
        if keep_logged == '1':
            self.username_entry.insert(0, f"{username}")
            self.password_entry.insert(0, f"{password}")
            self.keep_logged_ckb.select()
        
        
    def login_function(self, username, password, keep_logged, parent):
        global current_user_info
        self.log_response.destroy()
        # Checks to see if user wishes to remain logged in. Sets database value to "1" for user and "0" for others
        if keep_logged == 1:
            self.keep_logged_in(username)

        login_db_checker = Database(file_path_to_database)
        username_db, password_db = login_db_checker.login(username, password)
        if username_db == username and password_db == password:
            # Constructs dictionary with username and file/directory locations for access in second app. 
            current_user_info = self.initialize_user_information(username)
            self.controller.show_frame(Main_Page)
        else:
            error = login_error(username, password)
            self.log_response = tk.Label(self, text=error)
            self.log_response.grid(row=6, column=0, columnspan=2)
    
    def initialize_user_information(self, username):
        global current_user_info
        
        user_folder = f'{folder_path_to_database}\\{username}_Recipes'
        user_recipe_db = f'{user_folder}\\{username}.db'
        user_recipe_pictures = f'{user_folder}\\Recipe_Pictures'

        current_user_info['username'] = username
        current_user_info['recipe_folder_file_path'] = user_folder
        current_user_info['recipe_database_file_path'] = user_recipe_db
        current_user_info['recipe_picture_folder_file_path'] = user_recipe_pictures

        return current_user_info

    def keep_logged_in(self, username):
        login_db = Database(file_path_to_database)
        login_db.update_logged_in(username)

class AccountCreationPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        username_label = tk.Label(self, text='Username: ')
        username_label.grid(row=0, column=0, padx=10, sticky='w')
        self.username_entry = tk.Entry(self, width=30)
        self.username_entry.grid(row=0, column=1, padx=10)
        self.username_entry.focus()

        password_label = tk.Label(self, text='Password: ')
        password_label.grid(row=1, column=0, padx=10, sticky='w')
        self.password_entry = tk.Entry(self, show='*', width=30)
        self.password_entry.grid(row=1, column=1, padx=10)

        password_confirm_label = tk.Label(self, text='Password Confirm: ')
        password_confirm_label.grid(row=2, column=0, padx=10, sticky='w')
        self.password_confirm_entry = tk.Entry(self, show='*', width=30)
        self.password_confirm_entry.grid(row=2, column=1, padx=10)

        create_account_confirmation = tk.Button(self, text="Submit", command=lambda:
                                      self.account_creation_function(self.username_entry.get(),
                                      self.password_entry.get(), self.password_confirm_entry.get()))
        create_account_confirmation.grid(row=3, column=0, columnspan=2, pady=5)

        return_to_login_button = tk.Button(self, text='Return to Login', command=lambda: controller.show_frame(LoginPage))
        return_to_login_button.grid(row=4, column=0, columnspan=2, pady=10)

        self.account_creation_response = tk.Label(self, text='foo')

    def account_creation_function(self, username, password, password_confirmation):
        self.account_creation_response.destroy()
        
        user_folder = f'{folder_path_to_database}\\{username}_Recipes'
        user_recipe_db = f'{user_folder}\\{username}.db'
        user_recipe_pictures = f'{user_folder}\\Recipe_Pictures'

        if password == password_confirmation and len(username) > 3 and len(password) > 3 and not os.path.exists(user_folder):
            os.mkdir(user_folder)
            os.mkdir(user_recipe_pictures)
            db_log_writer = Database(file_path_to_database)
            db_log_writer.add_new_account(username, password, user_folder)
            db_recipe_writer = Database(user_recipe_db)
            db_recipe_writer.create_new_recipe_database(username)
            return self.controller.show_frame(LoginPage)
        else: # Error handling if username and password combination is too short, if password does not match, or username is taken
            text_response = account_creation_error(username, password, password_confirmation, user_folder)
            self.account_creation_response = tk.Label(self, text=text_response)
            self.account_creation_response.grid(row=5, column=0, columnspan=2, pady=10)

class Main_Page(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        self.welcome_label = tk.Label(self, text='Welcome to my cooking app. It is a WIP. Here are some pictures of food')
        self.welcome_label.grid(row=0, column=0, columnspan=4, sticky=tk.W)

        self.pic_frame = tk.Frame(self, width=300, height=100)
        self.pic_frame.grid(row=1, column=0, columnspan=4, sticky=tk.W)
'''
        self.pic_index = 0
        self.photos = [photo for photo in os.listdir(current_user_info['recipe_picture_folder_file_path']) if os.path.isfile]
        self.photo_length = len(self.photos)
        if self.photo_length > 0:
            self.display_picture = self.photos[self.pic_index]
            self.my_image = ImageTk.PhotoImage(Image.open(f"{current_user_info['recipe_picture_folder_file_path']}\\{self.display_picture}"))
            self.myLabel = tk.Label(self.pic_frame, image=self.my_image)
            self.myLabel.grid(row=1, column=0, columnspan=4)

            button_back = tk.Button(self.pic_frame, text='<', command=self.pic_previous)
            button_back.grid(row=3, column=1)
            button_forward = tk.Button(self.pic_frame, text='>', command=self.pic_forward)
            button_forward.grid(row=3, column=3)

            self.status = tk.Label(self.pic_frame, text=f'Image: {self.display_picture}', bd=1, relief=tk.SUNKEN)
            self.status.grid(row=4, column=0, columnspan=4)

    def pic_forward(self):
        self.myLabel.grid_forget()
        self.status.grid_forget()
        
        self.pic_index += 1
        self.display_picture = self.photos[self.pic_index]
        self.my_image = ImageTk.PhotoImage(Image.open(f"{current_user_info['recipe_picture_folder_file_path']}\\{self.display_picture}"))

        self.myLabel = tk.Label(self.pic_frame, image=self.my_image)
        self.myLabel.grid(row=1, column=0, columnspan=4)
        self.status = tk.Label(self.pic_frame, text=f'Image: {self.display_picture}', bd=1, relief=tk.SUNKEN)
        self.status.grid(row=4, column=0, columnspan=4)

    def pic_previous(self):
        self.myLabel.grid_forget()
        self.status.grid_forget()
        
        self.pic_index -= 1
        self.display_picture = self.photos[self.pic_index]
        self.my_image = ImageTk.PhotoImage(Image.open(f"{current_user_info['recipe_picture_folder_file_path']}\\{self.display_picture}"))

        self.myLabel = tk.Label(self.pic_frame, image=self.my_image)
        self.myLabel.grid(row=1, column=0, columnspan=4)
        self.status = tk.Label(self.pic_frame, text=f'Image: {self.display_picture}', bd=1, relief=tk.SUNKEN)
        self.status.grid(row=4, column=0, columnspan=4)
'''

class RecipeList(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

class Manual_Recipe_Adder(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        label_len = 23
        recipe_elements = ['ingredients', 'directions', 'notes']

        website_title_label = tk.Label(self, text='Website title (Ex. All Recipes): ', anchor='w', width=label_len)
        website_title_label.grid(row=0, column=0, columnspan=2, padx=5, pady=5)
        title_label = tk.Label(self, text='Recipe title: ', anchor='w', width=label_len)
        title_label.grid(row=1, column=0, columnspan=2, padx=5, pady=5)
        cuisine_label = tk.Label(self, text='Cuisine type (Ex. American): ', anchor='w', width=label_len)
        cuisine_label.grid(row=2, column=0, columnspan=2, padx=5, pady=5)
        cook_time_label = tk.Label(self, text='Cook Time (minutes, rounded): ', anchor='w', width=label_len)
        cook_time_label.grid(row=3, column=0, columnspan=2, padx=5, pady=5)
        servings_label = tk.Label(self, text='Servings (grams, rounded): ', anchor='w', width=label_len)
        servings_label.grid(row=4, column=0, columnspan=2, padx=5, pady=5)
        serving_size_label = tk.Label(self, text='Serving Size: ', anchor='w', width=label_len)
        serving_size_label.grid(row=5, column=0, columnspan=2, padx=5, pady=5)
        nutrition_info_label = tk.Label(self, text='Nutrition: ', anchor='w', width=label_len)
        nutrition_info_label.grid(row=6, column=0, columnspan=2, padx=5, pady=5)
        picture_label = tk.Label(self, text='Picture: ', anchor='w', width=label_len)
        picture_label.grid(row=7, column=0, columnspan=2, padx=5, pady=5)

        self.website_title_entry = tk.Entry(self)
        self.website_title_entry.grid(row=0, column=2, columnspan=2, padx=5, pady=5)
        self.title_entry = tk.Entry(self)
        self.title_entry.grid(row=1, column=2, columnspan=2, padx=5, pady=5)
        self.cuisine_entry = tk.Entry(self)
        self.cuisine_entry.grid(row=2, column=2, columnspan=2, padx=5, pady=5)
        self.cook_time_entry = tk.Entry(self)
        self.cook_time_entry.grid(row=3, column=2, columnspan=2, padx=5, pady=5)
        self.servings_entry = tk.Entry(self)
        self.servings_entry.grid(row=4, column=2, columnspan=2, padx=5, pady=5)
        self.serving_size_entry = tk.Entry(self)
        self.serving_size_entry.grid(row=5, column=2, columnspan=2, padx=5, pady=5)
        self.nutrition_info_entry = tk.Entry(self)
        self.nutrition_info_entry.grid(row=6, column=2, columnspan=2, padx=5, pady=5)
        self.picture_entry = tk.Entry(self)
        self.picture_entry.grid(row=7, column=2, columnspan=2, padx=5, pady=5)

        ingredients_label = tk.Label(self, text='Ingredients: ', anchor='w', width=label_len)
        ingredients_label.grid(row=8, column=0, columnspan=2, padx=5, pady=5)
        directions_label = tk.Label(self, text='Directions: ', anchor='w', width=label_len)
        directions_label.grid(row=9, column=0, columnspan=2, padx=5, pady=5)
        notes_label = tk.Label(self, text='Notes: ', anchor='w', width=label_len)
        notes_label.grid(row=10, column=0, columnspan=2, padx=5, pady=5)

        self.ingredients_entry = tk.Button(self, text='Add Ingredients', command=lambda: self.add_recipe_element_Ing_Dir_Note(parent, recipe_elements[0]))
        self.ingredients_entry.grid(row=8, column=2, columnspan=2, padx=5, pady=5)
        self.directions_entry = tk.Button(self, text='Add Directions', command=lambda: self.add_recipe_element_Ing_Dir_Note(parent, recipe_elements[1]))
        self.directions_entry.grid(row=9, column=2, columnspan=2, padx=5, pady=5)
        self.notes_entry = tk.Button(self, text='Add Notes', command=lambda: self.add_recipe_element_Ing_Dir_Note(parent, recipe_elements[2]))
        self.notes_entry.grid(row=10, column=2, columnspan=2, padx=5, pady=5)

        self.recipe_element_value = ['','','']

        '''recipe = [self.website_title_entry.get(), self.title_entry.get(), self.cuisine_entry.get(),
                  self.servings_entry.get(), self.serving_size_entry.get(), self.nutrition_info_entry.get(),
                  self.picture_entry.get(), self.recipe_element_value[0], self.recipe_element_value[1],
                  self.recipe_element_value[2]]'''

        self.submit_recipe_button = tk.Button(self, text='Add Recipe', command=lambda: self.create_recipe())
        self.submit_recipe_button.grid(row=11, column=0, columnspan=4)

        self.counter = 0

    def create_recipe(self):
        recipe = Recipe(self.website_title_entry.get(), self.title_entry.get(), self.cuisine_entry.get(),
                  self.cook_time_entry.get(), self.servings_entry.get(), self.serving_size_entry.get(),
                  self.nutrition_info_entry.get(), self.picture_entry.get(), self.recipe_element_value[0],
                  self.recipe_element_value[1], self.recipe_element_value[2])
        for k, v in vars(recipe).items():
            print(k, v)
        file_name = self.determine_file_name(recipe.title)
        rec_ID = self.determine_rec_ID() 
        self.file_writer(file_name, recipe)

    def determine_rec_ID(self):
        det_rec_ID_db = UserDatabase()
        rec_ID = det_rec_ID_db.rec_ID_return(set_db_path(folder_path_to_database))

    def determine_file_name(self, recipe):
        if not os.path.exists(f'{recipe}.txt'):
            file_name = f'{recipe}.txt'
        else:
            if os.path.exists(f'{recipe}.txt'):
                counter += 1
                if not os.path.exists(f'{recipe}_{counter}.txt'):
                    file_name = f'{recipe}_{counter}.txt'
                else:
                    self.determine_file_name(recipe)
        return file_name

    def file_writer(self, file_name, recipe):
        with open(file_name, 'w') as RecipeWriter:
            RecipeWriter.write(f'''Website title: {recipe[0]}
                                    Recipe title: {recipe[1]}

                                    Cuisine type: {recipe[2]}
                                    Servings: {recipe[5]}
                                    Serving Size: {recipe[4]}
                                    Cook time: {recipe[3]} minutes
                                    Nutrition info: {recipe[6]}

                                    Ingredients: {recipe[8]}
                                    Directions: {recipe[9]}
                                    Notes: {recipe[10]}
                                                ''')

    def add_recipe_element_Ing_Dir_Note(self, parent, recipe_element):
        top = tk.Toplevel(parent)

        self.recipe_element_label = tk.Label(top, text=recipe_element)
        self.recipe_element_label.grid(row=0, column=0)
        self.entry = tk.scrolledtext.ScrolledText(top, width=40, height=10)
        self.entry.grid(row=1, column=0)
        self.confirm_button = tk.Button(top, text=f"Add {recipe_element}", command=lambda: self.close(top, recipe_element))
        self.confirm_button.grid(row=2, column=0)

    def close(self, top, recipe_element):
        label_counter = ['ingredients', 'directions', 'notes'].index(f'{recipe_element}')
        row_number = label_counter + 8


        self.recipe_element_value[label_counter] = self.entry.get('1.0', tk.END)

        top.destroy()

        self.testlabel = tk.Label(self, text=f'{recipe_element} added')
        self.testlabel.grid(row=row_number, column=5, padx=5, pady=5)


    def add_recipe_to_folder(self):
        pass


    def add_recipe_attributes_to_recipe_browser(self):
        pass

class Recipe_Browser(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

    list_of_websites = []
    recipe_titles = []
    cuisine = []
    cook_times = []
    servings = []
    serving_sizes = []
    ingredients = []
    nutrition = []

    browse_by_recipe_elements = {'website_name': list_of_websites, 'title': recipe_titles, 'cuisine': cuisine,
                                 'cook_time': cook_times, 'servings': servings, 'serving_size': serving_sizes,
                                 'ingredients': ingredients, 'nutrition': nutrition}

class OnlineRecipeTool(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)


def main_program():
    startup_settings() 
    main_app = StartupGUI()
    main_app.title("Cookin' Bookin'")
    width, height = int(main_app.winfo_screenwidth()//1.5), int(main_app.winfo_screenheight()//1.5)
    main_app.geometry(f'{width}x{height}')
    main_app.mainloop()

if __name__ == "__main__":
    main_program()