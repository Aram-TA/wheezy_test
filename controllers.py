""" All controllers that application use during it's work
"""
import re
from datetime import datetime
from string import ascii_lowercase, ascii_uppercase, digits

from wheezy.core.collections import first_item_adapter
from wheezy.http import HTTPResponse
from wheezy.security import Principal
from werkzeug.security import check_password_hash, generate_password_hash

from data_base import db


class ErrorsController:
    @staticmethod    
    def render_http_error(
        status_code: int,
        options: dict,
        helpers: dict
    ) -> HTTPResponse:
        """Summary
        
        Parameters
        ----------
        status_code : int
            Status code of error that will be rendered.
        options : dict
            Default options dict from wheezy.http WSGIApplication
        helpers : dict
            Default dict of helpers from wheezy.web BaseHandler
        
        Returns
        -------
        HTTPResponse
            
        """
        assert status_code >= 400 and status_code <= 505

        response = HTTPResponse()
        response.status_code = status_code

        response.write(
            options["render_template"](
                f"errors/{status_code}.html", dict(helpers))
        )
        return response


class PageController:
    @staticmethod
    def init_pages(page: int) -> tuple[list, int]:
        """Summary
        
        Parameters
        ----------
        page : int
            Current page for user
        
        Returns
        -------
        tuple[list, int]
            items_on_page, total_pages

        """
        cursor = db.cursor()

        limit: int = 10
        offset: int = (page - 1) * limit

        items_on_page: list = cursor.execute(
            '''
            SELECT notes.id, notes.author_id, notes.title, notes.body,
            notes.created, users.username as creator
            FROM notes INNER JOIN users ON notes.author_id = users.id
            WHERE deleted = 0
            LIMIT ? OFFSET ?
            ''',
            (limit, offset)
        ).fetchall()

        posts_count: int = len(
            [post for post in cursor.execute('SELECT id FROM notes')]
        )
        total_pages = (posts_count + limit - 1) // limit if posts_count else 1

        cursor.close()
        return items_on_page, total_pages

    @staticmethod
    def define_current_page(query: str) -> int: 
        """ Validation for query string inside url. If it fails it returns 0
        
        Parameters
        ----------
        query : str
            Query string from user request
        
        Returns
        -------
        int

        """
        if (page := query.get("page", ["1"])[0]).isdigit():
            return int(page)
        return 0


class Searcher:
    @staticmethod
    def search_by_title_or_body(keyword: str) -> enumerate:
        """ Searches inside notes table from database, takes everything by
            keyword, returns it as enumerated list
        
        Parameters
        ----------
        keyword : str
            keyword from user input
        
        Returns
        -------
        enumerate
            enumerated list of search result

        """
        cursor = db.cursor()

        search_result = cursor.execute(
            '''
            SELECT * FROM notes WHERE (title LIKE ?1 OR body LIKE ?1)
            AND deleted = 0
            ''',
            (f"%{keyword}%",)
        ).fetchall()

        cursor.close()
        return enumerate(search_result, start=1)


class NotesController:
    __slots__ = ()

    @staticmethod
    def validate_post(
        post_id: str,
        user_session: None | dict = None
    ) -> dict | None:
        """ Validates post by id. If everything is ok returns it's data.
        
        Parameters
        ----------
        post_id : str
        user_session : None | dict, optional

        """
        cursor = db.cursor()

        current_post: dict = cursor.execute(
            'SELECT * FROM notes WHERE id = ?',
            (post_id,)
        ).fetchone()

        cursor.close()

        if not current_post:
            return

        if user_session and str(
                current_post["author_id"]) != user_session["user_id"]:
            return

        return current_post

    @staticmethod
    def delete_post(post_id: str):
        """ Deletes post from database
        
        Parameters
        ----------
        post_id : str
            
        """
        cursor = db.cursor()

        cursor.execute('UPDATE notes SET deleted = 1 WHERE id = ?', (post_id,))

        cursor.close()
        db.commit()

    @staticmethod
    def update_post(
        post_id: str,
        title: str,
        body: str
    ):
        """ Updates post by it's id and new data.
        
        Parameters
        ----------
        post_id : str
        title : str
            Title for updated version of post
        body : str
            Body for updated version of post

        """
        if not title:
            return "Title is required."

        cursor = db.cursor()

        cursor.execute(
            'UPDATE notes SET title = ?, body= ? WHERE id = ?',
            (title, body, post_id)
        )

        cursor.close()
        db.commit()

    @staticmethod
    def create_post(
        title: str,
        user_session: dict,
        body: str = ""
    ) -> None:
        """ Creates new post then writes it to database
        
        Parameters
        ----------
        title : str
            title for new post
        user_session : dict
            Current user data from session
        body : str
            body for new post

        """
        cursor = db.cursor()
        cursor.execute(
            '''INSERT INTO notes (
                title,
                body,
                created,
                author_id
            )
            VALUES (?, ?, ?, ?)''',
            (
                title,
                body,
                datetime.now().strftime("%Y-%m-%d %H:%M"),
                int(user_session['user_id'])
            )
        )

        cursor.close()
        db.commit()


class Users:
    __slots__ = ()

    @staticmethod
    def define_session(principal: Principal) -> dict:
        """Summary
        
        Parameters
        ----------
        principal : Principal
            Container for user sensitive session information
        
        Returns
        -------
        TYPE
            Description
        """
        if principal and (usr_id := principal.id):
            return {
                "user_id": usr_id,
                "username": principal.alias
            }

    @staticmethod
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
        cursor = db.cursor()

        cursor.execute(
            'SELECT id, username FROM users WHERE email = ?',
            (email,)
        )
        info = cursor.fetchone()
        cursor.close()

        return info

    @staticmethod
    def reg_new_acc(request_form: dict) -> None:
        """ Writes new account data into database.
        
        Parameters
        ----------
        request_form : dict
            Description
        """
        adapted_form = first_item_adapter(request_form)
        cursor = db.cursor()
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
        cursor.close()
        db.commit()

    @staticmethod
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

        cursor = db.cursor()

        if not cursor.execute(
            'SELECT id FROM users WHERE email = ?',
            (email,)
        ).fetchone():
            error = text

        else:
            password_hash = cursor.execute(
                'SELECT password FROM users WHERE email = ?',
                (email,)
            ).fetchone()[0]

            if not check_password_hash(
                password_hash,
                adapted_form["password"]
            ):
                error = text

        cursor.close()
        return error

    @classmethod
    def validate_registration(cls, request_form: dict) -> str | None:
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
        cursor = db.cursor()
        adapted_form = first_item_adapter(request_form)
        if cursor.execute(
            'SELECT id FROM users WHERE email = ? or phone_number = ?',
            (adapted_form["email"], adapted_form["phone_number"])
        ).fetchone():

            cursor.close()  # So I have to close it manually
            return "That email or phone number already exists."

        cursor.close()

        if adapted_form['password'] != adapted_form['password_repeat']:
            return "Passwords in both fields should be same."

        for input_type in ("email", "phone_number", "username", "password"):

            error: str | None
            if error := getattr(cls, f"validate_{input_type}")(
                adapted_form[input_type]
            ):
                return error

    @staticmethod
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

    @staticmethod
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
            return """Username should have length that is greater than 0 and
            less than 36 characters.""".strip()

        for char in username:
            if char not in allowed_characters:
                return """You used a character that is not allowed for username
                Please use latin letters and only underscore, hyphen,
                period are allowed from special characters.""".strip()

    @staticmethod
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

    @staticmethod
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
