import re
from datetime import datetime
from string import ascii_lowercase, ascii_uppercase, digits

from werkzeug.security import check_password_hash, generate_password_hash

from data_base import db


def init_pages(page: int) -> tuple[list, int]:
    """ Defines pages count, content, current page for application

    Parameters
    ----------
    page : int

    Returns
    -------
    tuple[list, int]

    """
    cursor = db.cursor()

    limit: int = 10
    offset: int = (page - 1) * limit

    items_on_page: list = cursor.execute(
        '''
        SELECT notes.id, notes.author_id, notes.title, notes.body,
        notes.created, users.username as creator
        FROM notes INNER JOIN users ON notes.author_id = users.id
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


def define_session(principal):
    if principal and (usr_id := principal.id):
        return {
            "user_id": usr_id,
            "username": principal.alias
        }


def define_current_page(query):
    if page := (query.get("page", ["1"])[0]).isdigit():
        return int(page)
    return 1


class Searcher:
    def search_by_title_or_body(self, keyword: str):
        cursor = db.cursor()

        search_result = cursor.execute(
            'SELECT * FROM notes WHERE title LIKE ?1 OR body LIKE ?1',
            (f"%{keyword}%",)
        ).fetchall()

        cursor.close()
        return enumerate(search_result, start=1)


class NotesController:
    """
    Class that validates, creates, deletes, and updates notes/posts
    """
    __slots__ = ()

    def validate_post(
        self,
        post_id: str,
        user_session: None | dict = None
    ) -> dict | None:
        """ Validates post id for usage. Returns current post if id is valid

        Parameters
        ----------
        post_id : str
        read_mode : bool

        Returns
        -------
        dict | None

        """
        cursor = db.cursor()

        current_post: dict = cursor.execute(
            'SELECT * FROM notes WHERE id = ?',
            (post_id,)
        ).fetchone()

        cursor.close()

        if not current_post:
            return

        if user_session:
            if str(current_post["author_id"]) != user_session["user_id"]:
                return

        return current_post

    def delete_post(self, post_id: str) -> None | str:
        """ Deletes post by id form database

        Parameters
        ----------
        post_id : str

        """
        cursor = db.cursor()

        cursor.execute('DELETE FROM notes WHERE id = ?', (post_id,))

        cursor.close()
        db.commit()

    def update_post(
        self,
        post_id: str,
        title: str,
        body: str
    ) -> None | str:
        """ Updates post by id

        Parameters
        ----------
        post_id : str
        title : str
        body : str

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

    def create_post(
        self,
        title: str,
        body: str,
        user_session: dict
    ) -> None:
        """ Creates new post, assigns id to it by using

        Parameters
        ----------
        title : str
        body : str

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
                user_session['user_id']
            )
        )

        cursor.close()
        db.commit()


class Users:
    __slots__ = ()

    def take_login_info(self, email: str):
        cursor = db.cursor()

        cursor.execute(
            'SELECT id, username FROM users WHERE email = ?',
            (email,)
        )
        info = cursor.fetchone()
        cursor.close()

        return info

    def reg_new_acc(self, request_form: dict) -> None:
        """ Registers new account data to database

        Parameters
        ----------
        request_form : dict

        """
        cursor = db.cursor()
        cursor.execute(
            '''INSERT INTO users (email, phone_number, username, password)
            VALUES (?, ?, ?, ?)''',
            (
                request_form["email"][0],
                request_form["phone_number"][0],
                request_form["username"][0],
                generate_password_hash(request_form["password"][0])
            )
        )
        cursor.close()
        db.commit()

    def validate_login(self, request_form: dict) -> str | None:
        """ Validates user login by using existing password and email.
        Also gives back user data for use to routing function

        Parameters
        ----------
        request_form : dict

        Returns
        -------
        str | None

        """
        error: str | None = None

        email: str = request_form["email"][0]
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
                request_form["password"][0]
            ):
                error = text

        cursor.close()
        return error

    def validate_registration(self, request_form: dict) -> None | str:
        """ Validates registration by using some functions above
            If we have some errors in validation we will receive error

        Parameters
        ----------
        request_form : dict

        Returns
        -------
        None | str

        """
        # Sqlite cursor doesn't support `with` context manager :(
        cursor = db.cursor()

        if cursor.execute(
            'SELECT id FROM users WHERE email = ? or phone_number = ?',
            (request_form["email"][0], request_form["phone_number"][0])
        ).fetchone():

            cursor.close()  # So I have to close it manually
            return "That email or phone number already exists."

        cursor.close()

        if request_form['password'][0] != request_form['password_repeat'][0]:
            return "Passwords in both fields should be same."

        for input_type in ("email", "phone_number", "username", "password"):

            error: str | None
            if error := getattr(self, f"validate_{input_type}")(
                request_form[input_type][0]
            ):
                return error

    def validate_phone_number(self, phone_number: str) -> None | str:
        """ Validates phone number

        Parameters
        -----------
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

    def validate_username(self, username: str) -> None | str:
        """ Validates username

        Parameters
        -----------
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

    def validate_password(self, password: str) -> None | str:
        """ Validates password.
            Function makes sure that password format is right

        Parameters
        -----------
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

    def validate_email(self, email: str) -> None | str:
        """ Validates email by using regex.

        Parameters
        ----------
        email : str

        Returns
        -------
        None | str

        """
        if not re.match(
                r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]{1,30}$",
                email
        ):
            return "Invalid email format. Please use correct email format."
