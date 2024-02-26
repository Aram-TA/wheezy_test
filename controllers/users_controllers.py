import re
from string import ascii_lowercase, ascii_uppercase, digits

from wheezy.security import Principal
from wheezy.core.collections import first_item_adapter
from werkzeug.security import generate_password_hash, check_password_hash

from data_base import db, CursorContextManager


def define_session(principal: Principal) -> dict | None:
    """ Returns dict of current connection session by using principal

    Parameters
    ----------
    principal : Principal
        Container for user sensitive session information

    Returns
    -------
    dict

    """
    if principal and (usr_id := principal.id):
        return {
            "user_id": usr_id,
            "username": principal.alias
        }


def take_login_info(email: str) -> tuple:
    """ Takes user info from database by email, returns it as tuple

    Parameters
    ----------
    email : str
        Email of user

    Returns
    -------
    tuple

    """
    with CursorContextManager(db) as cursor:
        cursor.execute(
            'SELECT id, username FROM users WHERE email = ?',
            (email,)
        )
        info = cursor.fetchone()

    return info


def reg_new_acc(request_form: dict) -> None:
    """ Writes new account data into database.

    Parameters
    ----------
    request_form : dict

    """
    adapted_form = first_item_adapter(request_form)

    with CursorContextManager(db) as cursor:
        cursor.execute(
            '''INSERT INTO users (email, phone_number, username, password)
            VALUES (?, ?, ?, ?)''',
            (
                adapted_form["email"],
                adapted_form["phone_number"],
                adapted_form["username"],
                generate_password_hash(adapted_form["password"])
            )
        )
    db.commit()


def validate_login(request_form: dict) -> str | None:
    """ Validates user login by using request_form

    Parameters
    ----------
    request_form : dict
        Form from user input inside client

    Returns
    -------
    str | None

    """
    error: str | None = None
    adapted_form = first_item_adapter(request_form)

    email: str = adapted_form["email"]
    text: str = "User with that email not found or Incorrect password"

    with CursorContextManager(db) as cursor:
        if not (
            password_hash := cursor.execute(
                'SELECT password FROM users WHERE email = ?',
                (email,)
            ).fetchone()[0]
        ) or not check_password_hash(
            password_hash,
            adapted_form["password"]
        ):
            error = text

    return error


def validate_registration(request_form: dict) -> str | None:
    """ Validates user registration by using request_form

    Parameters
    ----------
    request_form : dict
        Form from user input inside client

    Returns
    -------
    str | None
        Error from validation

    """
    with CursorContextManager(db) as cursor:
        adapted_form = first_item_adapter(request_form)

        if cursor.execute(
            'SELECT id FROM users WHERE email = ? or phone_number = ?',
            (adapted_form["email"], adapted_form["phone_number"])
        ).fetchone():
            return "That email or phone number already exists."

    if adapted_form['password'] != adapted_form['password_repeat']:
        return "Passwords in both fields should be same."

    for input, func in {
        "email": validate_email,
        "phone_number": validate_phone_number,
        "username": validate_username,
        "password": validate_password
    }.items():

        error: str | None
        if error := func(adapted_form[input]):
            return error


def validate_phone_number(phone_number: str) -> str | None:
    """ Validates phone number by using str.translate

    Parameters
    ----------
    phone_number : str

    Returns
    -------
    str | None

    """
    if not phone_number:
        return "Phone number can't be empty."

    cleaned_phone = phone_number.translate(str.maketrans("", "", "- +"))

    if not cleaned_phone.isdigit():
        return """You used a character that is not allowed for phone number
            Please use arabic digit. From special
            characters only underscore, space, period
            and plus are allowed from special characters.""".strip()

    number_length: int = len(cleaned_phone)

    if not (6 <= number_length <= number_length <= 36):
        return """Phone number should be longer that 6 characters
                and less than 37.""".strip()


def validate_username(username: str) -> str | None:
    """Validates username

    Parameters
    ----------
    username : str

    Returns
    -------
    str | None

    """
    allowed_characters: set = set(
        f"_-.{ascii_lowercase}{ascii_uppercase}{digits}"
    )
    usr_length: int = len(username)

    if usr_length < 2 or usr_length > 36:
        return """Username should have length that is greater than 2 and
        less than 36 characters.""".strip()

    for char in username:
        if char not in allowed_characters:
            return """You used a character that is not allowed for username
            Please use latin letters and only underscore, hyphen,
            period are allowed from special characters.""".strip()


def validate_password(password: str) -> str | None:
    """ Validates user password format

    Parameters
    ----------
    password : str

    Returns
    -------
    str | None

    """
    pwd_set: set = set(password)

    if not password:
        return "Password is required."

    if not pwd_set | set(ascii_lowercase):
        return "Password should contain at least 1 lowercase letters."

    if not pwd_set | set(ascii_uppercase):
        return "Password should contain at least 1 uppercase letters."

    if not pwd_set | set(digits):
        return "Password should contain at least 1 digit."

    if len(password) < 8:
        return "Password min length should be 8 characters."


def validate_email(email: str) -> str | None:
    """ Validates user email by using regex

    Parameters
    ----------
    email : str

    Returns
    -------
    str | None

    """
    if not re.match(
        r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]{1,30}$",
        email
    ):
        return "Invalid email format. Please use correct email format."
