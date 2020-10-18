import os


def account_creation_error(username: str, password: str, password_confirmation: str, user_folder: str) -> str:
    if len(username) < 4:
        text_response = "Please enter a 4 character or longer username."
    elif len(password) < 4:
        text_response = "Please enter a 4 character or longer password."
    elif password_confirmation != password:
        text_response = (
            "Password and confirmatory Password do not match, please try again."
        )
    elif os.path.exists(user_folder):
        text_response = (
            f"Username {username} already exists, please choose new username."
        )
    else:
        text_response = "Unknown error. Code is supposed to be unreachable."
    return text_response


def login_error(username: str, password: str) -> str:
    if username != "" and password != "":
        text_response = "No username and password combination found. Please try again."
    elif password != "":
        text_response = "Please enter username."
    elif username != "":
        text_response = "Please enter password."
    else:
        text_response = "Please enter a username and password."
    return text_response
