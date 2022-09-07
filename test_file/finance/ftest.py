#testing the logic and database space :)
#Bism Ellah Elra7mani Elra7eem
import os

from cs50 import SQL

from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd
# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

def register():
    """Register user"""
    # Update the data base with username and password (Don't forget to hash)

    username = input("please enter username: ")
    password = input("please enter password :")
    confirmation = input("please re-enter password :")
        #Checking username is not null or existed before
    if username == NULL:
        return "Username cannot be blank, please use a valid username."
    if username in db.execute("SELECT username FROM users"):
        return "Username already exist."

    if password != confirmation:
       return "The two passwords doesn't match, please enter same password."
    db.execute('INSERT INTO users (username, hash) VALUES (?,?)', username, generate_password_hash(password))
    return "you are registered"

print(register)