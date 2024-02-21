# from functools import wraps
# from typing import Callable


from wheezy.web import authorize
from wheezy.web.handlers import BaseHandler
from wheezy.security import Principal

# from flask import (
#     render_template,
#     Blueprint,
#     redirect,
#     request,
#     session,
#     url_for,
#     Response,
# )

from users import Users
from dataBase import db

# bp = Blueprint("auth", __name__, url_prefix="/auth")


class RegisterHandler(BaseHandler):
    def get(self):
        """ Renders register template

        Returns
        -------
        Response

        """
        return self.render_response("auth/register.html", error=None)

    def post(self):
        """ Does some validation for registration
        then if it succeed redirects to login

        Returns
        -------
        Response

        """
        users = Users()

        if error := users.validate_registration(self.request.form):
            return self.render_response("auth/register.html", error=error)

        users.reg_new_acc(self.request.form)

        return self.redirect_for("login")


class LoginHandler(BaseHandler):
    def get(self):
        """ Renders login template

        Returns
        -------
        Response

        """
        return self.render_response("auth/login.html", error=None)

    def post(self):
        """ Does some validation for login then if it succeed redirects
        to index page. Also handles current session of logged in user

        Returns
        -------
        Response

        """
        error = Users().validate_login(self.request.form)

        if error:
            return self.render_response("auth/login.html", error=error)

        cursor = db.cursor()

        cursor.execute(
            'SELECT id, username FROM users WHERE email = ?',
            (self.request.form['email'][0],)
        )
        user_id, username = cursor.fetchone()

        self.principal = Principal(id=f"{user_id},{username}")

        cursor.close()
        return self.redirect_for("home")


class LogOutHandler(BaseHandler):
    @authorize()
    def get(self):
        """ Clears all data of current flask
        session and redirects to index page

        Returns
        -------
        Response

        """
        del self.principal
        return self.redirect_for("home")
