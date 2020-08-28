import os


def account_creation_error(username, password, password_confirmation, user_folder):
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
        text_response = "Unknown error."
    return text_response


def login_error(username, password):
    if username != "" and password != "":
        text_response = "No username and password combination found. Please try again."
    elif password != "":
        text_response = "Please enter username."
    elif username != "":
        text_response = "Please enter password."
    else:
        text_response = "Please enter a username and password."
    return text_response
