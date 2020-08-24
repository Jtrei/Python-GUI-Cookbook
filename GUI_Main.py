import configparser
import sys
import io
import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText

from PIL import Image, ImageTk

from Accessory_Classes import *

from Error_Handling import *
from Extractor import *


# GLOBALS: Directories
folder_path_to_data_folder = os.path.join(os.getcwd(), 'Data')                                               # .\Data
folder_path_to_configuration_directory = os.path.join(folder_path_to_data_folder, 'Configuration')           # .\Data\Configuration
folder_path_to_database = os.path.join(folder_path_to_data_folder, 'Database')                          # .\Data\Database
# Files
file_path_to_database: str = os.path.join(folder_path_to_database, 'Global.db')                              # .\Data\Database\Global.db
# Data Structures
current_user_info: dict = {'username':'','recipe folder file path':'','recipe picture folder file path':''}
database = Database(file_path_to_database)
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
        database.initialize()

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

        upper_menu_bar = tk.Menu(container)
        tk.Tk.config(self, menu=upper_menu_bar)
        
        recipe_sub_menu = tk.Menu(upper_menu_bar, tearoff=0)
        upper_menu_bar.add_cascade(label='Recipes', menu=recipe_sub_menu)
        recipe_sub_menu.add_command(label='Add recipe', command=lambda: self.menu_check(Manual_Recipe_Adder))
        recipe_sub_menu.add_command(label='Add recipe from website', command=lambda: self.menu_check(Online_Recipe_Adder)) 
        recipe_sub_menu.add_command(label='Browse recipes', command=lambda: self.menu_check(Recipe_Browser)) 
        recipe_sub_menu.add_command(label='Import Recipes (from text file)', command=lambda: self.menu_check(Import_Recipes_From_Text)) 
        recipe_sub_menu.add_command(label='Export Recipes (to PDF)', command=lambda: self.menu_check(Export_Recipe_To_PDF))  
        edit_sub_menu = tk.Menu(upper_menu_bar, tearoff=0)
        upper_menu_bar.add_cascade(label='Edit', menu=edit_sub_menu)
        edit_sub_menu.add_command(label='Edit Recipe', command=Edit_Recipe) 
        edit_sub_menu.add_command(label='Edit Settings', command=Edit_Settings) 
        edit_sub_menu.add_command(label='Edit View', command=Edit_View)  

        self.frames = {}
        gui_frames = [LoginPage, AccountCreationPage, Main_Page, Manual_Recipe_Adder, Online_Recipe_Adder, Recipe_Browser, Import_Recipes_From_Text, Export_Recipe_To_PDF,
                      Edit_Recipe, Edit_Settings, Edit_View]
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
        #If the user has not logged in yet and updated their current user info, the menu should not lead to additional pages.
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
        username, password, keep_logged = database.query_on_startup()
        if keep_logged == '1':
            self.username_entry.insert(0, f"{username}")
            self.password_entry.insert(0, f"{password}")
            self.keep_logged_ckb.select()
        
    def login_function(self, username, password, keep_logged):
        global current_user_info
        try:
            username_db, password_db = database.login(username, password)
            if username_db == username and password_db == password: 
                if keep_logged == 1:
                    # Checks to see if user wishes to remain logged in. Sets database value to "1" for user and "0" for others
                    database.update_logged_in(username)
                current_user_info['username'] = username
                current_user_info['recipe folder file path'] = f'{folder_path_to_database}\\{username}_Recipes'
                current_user_info['recipe picture folder file path'] = f"{current_user_info['recipe folder file path']}\\Recipe_Pictures"
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

        for i, label_name in enumerate(['Username: ', 'Password: ', 'Password Confirm: ']):
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
            database.add_new_account(username, password)
            database.create_new_recipe_table(username)
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
        self.status = tk.Label(self)

        self.pic_index = 0

        try:
            byte_photo_data = database.return_photo_list()
            self.photos = [io.BytesIO(photo) for photo in byte_photo_data]
            self.photo_length = len(self.photos)
            self.welcome_label = tk.Label(self, text="Welcome to my cooking app. Looks yummy.")
            self.welcome_label.grid(row=0, column=0, columnspan=4, sticky=tk.W)
            self.display_picture = self.photos[self.pic_index]
            self.my_image = ImageTk.PhotoImage(self.display_picture)
            self.myLabel = tk.Label(self, image=self.my_image)
            self.myLabel.grid(row=1, column=0, columnspan=4)

            button_back = tk.Button(self, text='<', command=self.pic_change('backward'))
            button_back.grid(row=3, column=1)
            button_forward = tk.Button(self, text='>', command=self.pic_change('forward'))
            button_forward.grid(row=3, column=3)

            self.status = tk.Label(self, text=f'Image: {self.display_picture}', bd=1, relief=tk.SUNKEN)
            self.status.grid(row=4, column=0, columnspan=4)
        except (IndexError or sql.OperationalError):
            self.welcome_label = tk.Label(self, text="Welcome to my cooking app. It is a WIP. All user's photos will appear here once you add some recipes")
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

class Manual_Recipe_Adder(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        element_length = 25
        self.widget_entry = {}
        widgets_text = {'website':'Website title (Ex. All Recipes):','title':'Recipe title:','cuisine':'Cuisine type (Ex. American):','cook time':'Cook Time (minutes, rounded):',
                        'servings':'Servings (grams, rounded):','serving size': 'Serving size: ','picture':'Picture:','ingredients':'Ingredients:','directions':'Directions:','nutrition':'Nutrition:',
                        'notes':'Notes:'}
        self.long_response_recipe_components = {'ingredients':'','directions':'','nutrition':'','notes':''}
        for i, (key, value) in enumerate(widgets_text.items()):
            self.label = tk.Label(self, text=value, anchor='w', width=element_length)
            self.label.grid(row=i, column=0, padx=5, pady=5)
            if key not in list(self.long_response_recipe_components.keys()):
                self.widget_entry[key] = tk.Entry(self, width=element_length)
                self.widget_entry[key].grid(row=i, column=1, padx=x_in, pady=y_down)
            else:
                self.widget_entry[key] = tk.Button(self, text=f'Add {key}', command=lambda: self.popup_for_longer_entries(parent, key, i), width=element_length)
                self.widget_entry[key].grid(row=i, column=1, columnspan=2, padx=x_in, pady=y_down)

        submit_recipe_button = tk.Button(self, text='Add Recipe', command=lambda: self.create_recipe())
        submit_recipe_button.grid(row=11, column=0, columnspan=4)

    def create_recipe(self):
        self.log_response = tk.Label(self, text='Dummy response whose only purpose is to be destroyed') 

        def convert_picture_path_to_binary_data(file_path):
            while True:
                self.log_response.destroy()
                if file_path != '':
                    try:
                        with open(file_path, 'rb') as binary_reader:
                            binary_data = binary_reader.read()
                            return binary_data
                    except FileNotFoundError:
                        self.log_response = tk.Label(self, text='Picture file not found. Please check file location again or leave space blank')
                        self.log_response.grid(row=12, column=0, columnspan=2, padx=x_in, sticky='w')
                else: 
                    break

        picture_binary_data = convert_picture_path_to_binary_data(self.widget_entry['picture'].get())

        recipe = Recipe(self.widget_entry['website'].get(), self.widget_entry['title'].get(), self.widget_entry['cuisine'].get(),
                self.widget_entry['cook time'].get(), self.widget_entry['servings'].get(), self.widget_entry['serving size'].get(),
                self.long_response_recipe_components['ingredients'], self.long_response_recipe_components['directions'],
                self.long_response_recipe_components['nutrition'], self.long_response_recipe_components['notes'], picture_binary_data)

        database.write_recipe_to_database(recipe, current_user_info['username'])

        self.file_writer(recipe)

        self.log_response = tk.Label(self, text='Recipe Added!')
        self.log_response.grid(row=12, column=0, columnspan=2, padx=x_in, sticky='w')

    def file_writer(self, recipe):
        os.chdir(current_user_info['recipe folder file path'])
        
        def determine_unique_file_name(recipe_title):
            duplicate_recipe_name_counter = 1
            if not os.path.exists(f'{recipe_title}.txt'):
                file_name = f'{recipe_title}.txt'
            else:
                while True:
                    duplicate_recipe_name_counter += 1
                    if not os.path.exists(f'{recipe_title}_{duplicate_recipe_name_counter}.txt'):
                        file_name = f'{recipe_title}_{duplicate_recipe_name_counter}.txt'
                        break
            return file_name

        file_name = determine_unique_file_name(recipe.title)

        with open(file_name, 'w') as RecipeWriter:
            RecipeWriter.write(f'''
Website name: {recipe.website_name}
Recipe title: {recipe.title}\n
Cuisine type: {recipe.cuisine}
Servings: {recipe.servings}
Serving Size: {recipe.serving_size}
Cook time: {recipe.cook_time} minutes
Nutrition info: {recipe.nutrition_info}\n
Ingredients: {recipe.ingredients}
Directions: {recipe.directions}
Notes: {recipe.notes}
                                ''')

    def popup_for_longer_entries(self, parent, recipe_element, index):
        top = tk.Toplevel(parent)

        self.recipe_element_label = tk.Label(top, text=recipe_element)
        self.recipe_element_label.grid(row=0, column=0)
        self.entry = tk.scrolledtext.ScrolledText(top, width=40, height=10)
        self.entry.grid(row=1, column=0)
        self.confirm_button = tk.Button(top, text=f"Add {recipe_element}", command=lambda: close(top, recipe_element, index))
        self.confirm_button.grid(row=2, column=0)

        def close(top, recipe_element, index):
            self.long_response_recipe_components[index] = self.entry.get('1.0', tk.END)
            top.destroy()


    def add_recipe_to_folder(self):
        pass


    def add_recipe_attributes_to_recipe_browser(self):
        pass

class Online_Recipe_Adder(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

class Recipe_Browser(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

class Import_Recipes_From_Text(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

class Export_Recipe_To_PDF(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

class Edit_Recipe(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

class Edit_Settings(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

class Edit_View(tk.Frame):
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
