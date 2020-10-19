import os
from src.Accessory_Classes import Database
import configparser

# ------------------------------------------------GLOBALS:
# -----------------Directories
folder_path_to_data_folder: str = os.path.join(os.getcwd(), "Data")
# .\Data
folder_path_to_configuration_directory: str = os.path.join(
    folder_path_to_data_folder, "Configuration"
)
# .\Data\Configuration
folder_path_to_database: str = os.path.join(
    folder_path_to_data_folder, "Database"
)
# .\Data\Database

# ----------------- Files
file_path_to_database: str = os.path.join(
    folder_path_to_database, "Global.db"
)  # .\Data\Database\Global.db

# -----------------Data Structures
current_user_info: dict = {
    "username": "",
    "recipe folder file path": "",
    "recipe picture folder file path": "",
}
database = Database(file_path_to_database)


# --- Startup Functions --- Create directories, files, and database if not already existing
def startup_settings() -> None:
    if os.path.exists(
        os.path.join(folder_path_to_configuration_directory, "Configuration.ini")
    ):
        pass
    elif not os.path.exists(folder_path_to_data_folder):
        os.mkdir(folder_path_to_data_folder)
        os.mkdir(folder_path_to_configuration_directory)
        os.mkdir(folder_path_to_database)
        database.initialize()

        os.chdir(folder_path_to_configuration_directory)

        config = configparser.ConfigParser()
        config["Folder Paths"] = {
            "Data": folder_path_to_data_folder,
            "Configuration": folder_path_to_configuration_directory,
            "Database": folder_path_to_database,
        }
        config["File Paths"] = {"Database": file_path_to_database}
        with open("Configuration.ini", "w") as config_file:
            config.write(config_file)
