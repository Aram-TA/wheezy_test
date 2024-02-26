from wheezy.web.handlers import BaseHandler
from wheezy.http import HTTPResponse
from wheezy.web import authorize
from wheezy.security import Principal

from controllers.users_controllers import (
    validate_registration,
    reg_new_acc,
    validate_login,
    take_login_info
)


class RegisterHandler(BaseHandler):
    def get(self) -> HTTPResponse:
        """ Renders register html

        Returns
        -------
        HTTPResponse
            Wheezy.http response object

        """
        return self.render_response("register.html", error=None)

    def post(self) -> HTTPResponse:
        """ Validates registration form, if everything is ok registers new
            user to database. Then redirects to login page.

        Returns
        -------
        HTTPResponse
            Wheezy.http response object
        """
        request_form = self.request.form

        if error := validate_registration(request_form):
            return self.render_response("register.html", error=error)

        reg_new_acc(request_form)

        return self.redirect_for("login")


class LoginHandler(BaseHandler):
    def get(self) -> HTTPResponse:
        """ Renders login html

        Returns
        -------
        HTTPResponse
            Wheezy.http response object

        """
        return self.render_response("login.html", error=None)

    def post(self) -> HTTPResponse:
        """ Validates login form, if everything is ok redirects to home page.

        Returns
        -------
        HTTPResponse
            Wheezy.http response object

        """
        request_form = self.request.form

        if error := validate_login(request_form):
            return self.render_response("login.html", error=error)

        user_id, username = take_login_info(
            request_form["email"][0]
        )
        self.principal = Principal(id=str(user_id), alias=username)

        return self.redirect_for("home")


class LogOutHandler(BaseHandler):
    @authorize()
    def get(self) -> HTTPResponse:
        """ Deletes principal object, which is authentication cookie
            inside browser

        Returns
        -------
        HTTPResponse
            Wheezy.http response object

        """
        del self.principal
        return self.redirect_for("home")
