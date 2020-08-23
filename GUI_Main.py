import configparser
import sys
import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText

from PIL import Image, ImageTk

from Class_Database import *
from Class_Recipe import *
from Error_Handling import *
from Extractor import *


# GLOBALS: Directories
folder_path_to_data_folder = os.path.join(os.getcwd(), 'Data')                                               # .\Data
folder_path_to_configuration_directory = os.path.join(folder_path_to_data_folder, 'Configuration')           # .\Data\Configuration
folder_path_to_database: str = os.path.join(folder_path_to_data_folder, 'Database')                          # .\Data\Database
# Files
file_path_to_database: str = os.path.join(folder_path_to_database, 'Global.db')                              # .\Data\Database\Global.db
# Data Structures
current_user_info: dict = {'username':'','recipe folder file path':'','recipe database file path':'','recipe picture folder file path':''}
# Widget_positioning
x_in = 10
y_down = 3


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

        def submenu_configuration(submenu_items, menu):
            for i, (key, value) in enumerate(submenu_items.items()):
                menu.add_command(label=key, command=lambda: self.menu_check(value))    

        container = tk.Frame(self)
        container.pack(side="top", fill='both', expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        upper_menu_bar = tk.Menu(container)
        tk.Tk.config(self, menu=upper_menu_bar)
        drop_down_headers = ('Recipes', 'Edit')
        
        recipe_sub_menu = tk.Menu(upper_menu_bar, tearoff=0)
        recipe_submenu_buttons = {'Add recipe': Manual_Recipe_Adder, 'Add recipe from website': OnlineRecipeTool, 'Browse recipes': RecipeList,
                                  'Import Recipes (from text file)': '', 'Export Recipes (to PDF)': ''}
        submenu_configuration(recipe_submenu_buttons, recipe_sub_menu)
        upper_menu_bar.add_cascade(label='Recipes', menu=recipe_sub_menu)

        edit_sub_menu = tk.Menu(upper_menu_bar, tearoff=0)
        edit_submenu_buttons = {'Edit Recipe': '', 'Edit Settings': '', 'Edit View': ''}
        submenu_configuration(edit_submenu_buttons, edit_sub_menu)
        upper_menu_bar.add_cascade(label=drop_down_headers[1], menu=edit_sub_menu)


        self.frames = {}
        gui_frames = [LoginPage, AccountCreationPage, Main_Page, Recipe_Browser, OnlineRecipeTool, Manual_Recipe_Adder]
        for Frame in gui_frames: 
            frame = Frame(container, self) 
            self.frames[Frame] = frame # self.frames[LoginPage] = LoginPage[container, self]
            frame.grid(row=0, column=0, sticky='nsew')

        # Start program by showing login page
        self.show_frame(LoginPage)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()            

    def menu_check(self, page):
        # If the user has not logged in yet and updated their current user info, the menu should not lead to additional pages.
        if current_user_info['username'] != '':
            self.show_frame(page)

class LoginPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        username_label = tk.Label(self, text='Username: ')
        username_label.grid(row=0, column=0, pady=(10, 0), padx=10, sticky='w')
        self.username_entry = tk.Entry(self, width=30)
        self.username_entry.grid(row=0, column=1, padx=x_in)
        self.username_entry.focus()

        password_label = tk.Label(self, text='Password: ')
        password_label.grid(row=1, column=0, padx=x_in, sticky='w')
        self.password_entry = tk.Entry(self, show='*', width=30)
        self.password_entry.grid(row=1, column=1, padx=x_in)

        var1 = tk.IntVar()
        self.keep_logged_ckb = tk.Checkbutton(self, text='Keep signed in?', variable=var1, onvalue=1, offvalue=0)
        self.keep_logged_ckb.grid(row=2, column=1, padx=x_in, pady=y_down, sticky='w'+'e')

        enter_login = tk.Button(self, text="Submit", command=lambda: self.login_function(self.username_entry.get(), self.password_entry.get(), var1.get()))
        enter_login.grid(row=3, column=1, padx=x_in, pady=y_down, sticky='w'+'e')
        create_account = tk.Button(self, text='Create Account', command=lambda: controller.show_frame(AccountCreationPage))
        create_account.grid(row=4, column=1, padx=x_in, pady=y_down, sticky='w'+'e')

        # Searches login database to see if previous user wanted to remain logged in. The .keep_logged_in method below
        # ensures that only one user will have a "1" value in the database column for keep_logged. If so, the fields will
        # become pre-populated.
        database_query = Database(file_path_to_database)
        username, password, keep_logged = database_query.query_on_startup()
        if keep_logged == '1':
            self.username_entry.insert(0, f"{username}")
            self.password_entry.insert(0, f"{password}")
            self.keep_logged_ckb.select()
        
    def login_function(self, username, password, keep_logged):
        global current_user_info
        login_database_checker_updater = Database(file_path_to_database)
        try:
            username_db, password_db = login_database_checker_updater.login(username, password)
            if username_db == username and password_db == password: 
                if keep_logged == 1:
                    # Checks to see if user wishes to remain logged in. Sets database value to "1" for user and "0" for others
                    login_database_checker_updater.update_logged_in(username)
                current_user_info['username'] = username
                current_user_info['recipe folder file path'] = f'{folder_path_to_database}\\{username}_Recipes'
                current_user_info['recipe database file path'] = f'{user_folder}\\{username}.db'
                current_user_info['recipe picture folder file path'] = f'{user_folder}\\Recipe_Pictures'
                self.controller.show_frame(Main_Page)
        # Occurs when there is no database match resulting in no return of username_db and password_db
        except TypeError: 
            error = login_error(username, password)
            self.log_response = tk.Label(self, text='Dummy response whose only purpose is to be destroyed') 
            self.log_response.destroy()
            self.log_response = tk.Label(self, text=error)
            self.log_response.grid(row=6, column=0, columnspan=2, padx=x_in, sticky='w')

class AccountCreationPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        labels = ['Username: ', 'Password: ', 'Password Confirm: ']
        for i, label_name in enumerate(labels):
            label = tk.Label(self, text=label_name)
            label.grid(row=i, column=0, padx=x_in, pady=y_down, sticky='w')

        username_entry = tk.Entry(self, width=30)
        username_entry.grid(row=0, column=1, padx=x_in, pady=y_down)
        username_entry.focus()
        password_entry = tk.Entry(self, show='*', width=30)
        password_entry.grid(row=1, column=1, padx=x_in, pady=y_down)
        password_confirm_entry = tk.Entry(self, show='*', width=30)
        password_confirm_entry.grid(row=2, column=1, padx=x_in, pady=y_down)

        return_to_login_button = tk.Button(self, text='Return to Login', command=lambda: controller.show_frame(LoginPage))
        return_to_login_button.grid(row=3, column=0, columnspan=1, padx=x_in, pady=y_down, sticky='w'+'e')
        create_account_confirmation = tk.Button(self, text="Submit", command=lambda: self.account_creation_function(username_entry.get(), password_entry.get(), password_confirm_entry.get()))
        create_account_confirmation.grid(row=3, column=1, columnspan=1, padx=x_in, pady=y_down, sticky='w'+'e')

    def account_creation_function(self, username, password, password_confirmation):        
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
            self.account_creation_response = tk.Label(self, text='Dummy response whose only purpose is to be destroyed')
            self.account_creation_response.destroy()
            self.account_creation_response = tk.Label(self, text=text_response)
            self.account_creation_response.grid(row=5, column=0, columnspan=4, padx=x_in, pady=y_down, sticky='w')

class Main_Page(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        self.pic_index = 0



        # Eventual plans will have the main page access the database and pull photos from the user's recipe collection
        '''
        self.photos = [photo for photo in os.listdir(current_user_info['recipe picture folder file path']) if os.path.isfile]
        self.photo_length = len(self.photos)
        if self.photo_length > 0:
            self.welcome_label = tk.Label(self, text="Welcome to my cooking app. Looks yummy.")
            self.welcome_label.grid(row=0, column=0, columnspan=4, sticky=tk.W)
            self.display_picture = self.photos[self.pic_index]
            self.my_image = ImageTk.PhotoImage(Image.open(f"{current_user_info['recipe picture folder file path']}\\{self.display_picture}"))
            self.myLabel = tk.Label(self, image=self.my_image)
            self.myLabel.grid(row=1, column=0, columnspan=4)

            button_back = tk.Button(self, text='<', command=self.pic_previous('backward'))
            button_back.grid(row=3, column=1)
            button_forward = tk.Button(self, text='>', command=self.pic_forward('forward'))
            button_forward.grid(row=3, column=3)

            self.status = tk.Label(self, text=f'Image: {self.display_picture}', bd=1, relief=tk.SUNKEN)
            self.status.grid(row=4, column=0, columnspan=4)
        else:
            self.welcome_label = tk.Label(self, text="Welcome to my cooking app. It is a WIP. Your recipe's photos will appear here once you add some recipes")
            self.welcome_label.grid(row=0, column=0, columnspan=4, sticky=tk.W)
            

    def pic_change(self, val):
        self.myLabel.grid_forget()
        self.status.grid_forget()
        if val == 'forward':
            self.pic_index += 1
        elif val == 'backward':
            self.pic_index -= 1
        self.display_picture = self.photos[self.pic_index]
        self.my_image = ImageTk.PhotoImage(Image.open(f"{current_user_info['recipe picture folder file path']}\\{self.display_picture}"))

        self.myLabel = tk.Label(self, image=self.my_image)
        self.myLabel.grid(row=1, column=0, columnspan=4)
        self.status = tk.Label(self, text=f'Image: {self.display_picture}', bd=1, relief=tk.SUNKEN)
        self.status.grid(row=4, column=0, columnspan=4)
        '''

class RecipeList(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

class Manual_Recipe_Adder(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        element_length = 25
        widget_entry = {}
        widgets_text = {'website':'Website title (Ex. All Recipes):','title':'Recipe title:','cuisine':'Cuisine type (Ex. American):','cook time':'Cook Time (minutes, rounded):',
                        'servings':'Servings (grams, rounded):','nutrition':'Nutrition:','picture':'Picture:','ingredients':'Ingredients:', 'directions':'Directions:','notes':'Notes:'}
        for i, (key, value) in enumerate(widgets_text.items()):
            label = tk.Label(self, text=value, anchor='w', width=element_length)
            label.grid(row=i, column=0, padx=5, pady=5)
            if key not in ['ingredients', 'directions', 'notes']:
                widget_entry[key] = tk.Entry(self, width=element_length)
                widget_entry[key].grid(row=i, column=1, padx=x_in, pady=y_down)
            else:
                widget_entry[key] = tk.Button(self, text=f'Add {key}', command=lambda: self.add_long_recipe_element(parent, key), width=element_length)
                widget_entry[key].grid(row=i, column=1, columnspan=2, padx=x_in, pady=y_down)

        self.recipe_element_value = ['','','']
        self.submit_recipe_button = tk.Button(self, text='Add Recipe', command=lambda: self.create_recipe())
        self.submit_recipe_button.grid(row=11, column=0, columnspan=4)

        self.counter = 1

    def create_recipe(self):
        with open(self.picture_entry.get(), 'rb') as binary_reader:
            self.picture_entry = binary_reader.read()

        recipe = Recipe(self.website_title_entry.get(), self.title_entry.get(), self.cuisine_entry.get(),
                  self.cook_time_entry.get(), self.servings_entry.get(), self.serving_size_entry.get(),
                  self.nutrition_info_entry.get(), self.picture_entry, self.recipe_element_value[0],
                  self.recipe_element_value[1], self.recipe_element_value[2])
        file_name = self.determine_file_name(recipe.title)
        rec_ID = self.determine_rec_ID() 
        self.file_writer(file_name, recipe)

    def determine_rec_ID(self):
        unique_database_ID = Database(file_path_to_database)
        rec_ID = unique_database_ID.rec_ID_return()

    def determine_file_name(self, recipe):
        if not os.path.exists(f'{recipe}.txt'):
            file_name = f'{recipe}.txt'
        else:
            while True:
                self.counter += 1
                if not os.path.exists(f'{recipe}_{self.counter}.txt'):
                    file_name = f'{recipe}_{self.counter}.txt'
                    self.counter = 1
                    break
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

    def add_long_recipe_element(self, parent, recipe_element):
        top = tk.Toplevel(parent)

        self.recipe_element_label = tk.Label(top, text=recipe_element)
        self.recipe_element_label.grid(row=0, column=0)
        self.entry = tk.scrolledtext.ScrolledText(top, width=40, height=10)
        self.entry.grid(row=1, column=0)
        self.confirm_button = tk.Button(top, text=f"Add {recipe_element}", command=lambda: close(top, recipe_element))
        self.confirm_button.grid(row=2, column=0)

        def close(top, recipe_element):
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

class OnlineRecipeTool(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)


def main_program():
    startup_settings() 
    main_app = StartupGUI()
    main_app.title("Cookin' Bookin'")
    width, height = int(main_app.winfo_screenwidth()//1.5), int(main_app.winfo_screenheight()//1.5)
    main_app.geometry(f'400x400')
    main_app.mainloop()

if __name__ == "__main__":
    main_program()
