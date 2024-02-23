"""Summary
"""
from wheezy.http import HTTPResponse
from wheezy.web import authorize
from wheezy.web.handlers import BaseHandler
from wheezy.security import Principal
from wheezy.core.collections import first_item_adapter

from controllers import (
    PageController,
    Searcher,
    NotesController,
    Users,
    ErrorsController
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
        users = Users()

        if error := users.validate_registration(self.request.form):
            return self.render_response("register.html", error=error)

        users.reg_new_acc(self.request.form)

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
        users = Users()

        if error := users.validate_login(self.request.form):
            return self.render_response("login.html", error=error)

        user_id, username = users.take_login_info(
            self.request.form["email"][0]
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


class IndexHandler(BaseHandler):
    def get(self) -> HTTPResponse:
        """ Basically redirects to home page from index 
        
        Returns
        -------
        HTTPResponse
            Wheezy.http response object

        """
        return self.redirect_for("home")


class HomeHandler(BaseHandler):
    def get(self) -> HTTPResponse:
        """ Handles pagination, renders home page
        
        Returns
        -------
        HTTPResponse
            Wheezy.http response object

        """
        page: int = PageController.define_current_page(self.request.query)
        items_on_page, total_pages = PageController.init_pages(page)

        # TODO put here 404
        if page > total_pages or page < 1:
            return ErrorsController.render_http_error(
                404,
                self.options,
                self.helpers
            )

        return self.render_response(
            "home.html",
            items_on_page=items_on_page,
            total_pages=total_pages,
            page=page,
            user_session=Users.define_session(self.principal)
        )


class SearchHandler(BaseHandler):
    def get(self) -> HTTPResponse:
        """ Renders search page
        
        Returns
        -------
        HTTPResponse
            Wheezy.http response object

        """
        return self.render_response("search.html", search_result=None)

    def post(self) -> HTTPResponse:
        """ Searches inside database post with keyword
            Renders response with founded resources.
        
        Returns
        -------
        HTTPResponse
            Wheezy.http response object

        """
        keyword: str = self.request.form["search_keyword"][0]
        search_result = Searcher().search_by_title_or_body(keyword)

        return self.render_response(
            "search.html",
            search_result=search_result
        )


class ReadPostHandler(BaseHandler):
    def get(self) -> HTTPResponse:
        """ Gives back html for read-post dialogue.
            Supposed to be used with XHR.
        
        Returns
        -------
        HTTPResponse
            Wheezy.http response object

        """
        post_id: str = str(self.route_args.get("post_id"))

        if not (
            current_post := NotesController().validate_post(post_id)
        ):
            return self.redirect_for("home")

        return self.render_response(
            "read-post.html",
            post=current_post,
        )


class CreatePostHandler(BaseHandler):
    @authorize
    def get(self) -> HTTPResponse:
        """ Renders creating page
        
        Returns
        -------
        HTTPResponse
            Wheezy.http response object

        """
        return self.render_response("create.html", error=None)

    @authorize()
    def post(self) -> HTTPResponse:
        """ Validates info from user, if everything is ok
            redirects to home page. Shows error inside create page
            if validation isn't passed. 
        
        Returns
        -------
        HTTPResponse
            Wheezy.http response object

        """
        adapted_form = first_item_adapter(self.request.form)
        if not (title := adapted_form["title"]):
            return self.render_response(
                "create.html",
                error="Title is required"
            )

        NotesController().create_post(
            title,
            Users.define_session(self.principal),
            adapted_form["body"],
        )

        return self.redirect_for("home")


class UpdatePostHandler(BaseHandler):
    @authorize
    def get(self) -> HTTPResponse:
        """ Renders post updating and deleting page after
        post id and user validation.
        
        Returns
        -------
        HTTPResponse
            Wheezy.http response object

        """
        if not (
            current_post := NotesController().validate_post(
                str(self.route_args.get("post_id")),
                Users.define_session(self.principal)
            )
        ):
            return self.redirect_for("home")

        return self.render_response(
            "update.html",
            current_post=current_post,
            error=None
        )

    @authorize
    def post(self) -> HTTPResponse:
        """ Validates post id and form that user passed. If everything is ok
            Updates post then returns to home page. Shows error inside
            update page if validation isn't passed. 
        
        Returns
        -------
        HTTPResponse
            Wheezy.http response object

        """
        notes_controller = NotesController()
        adapted_form = first_item_adapter(self.request.form)
        post_id: str = str(self.route_args.get("post_id"))

        if (
            current_post := notes_controller.validate_post(
                post_id,
                Users.define_session(self.principal)
                )
        ) and (
            error := notes_controller.update_post(
                post_id,
                adapted_form["title"],
                adapted_form["body"]
            )
        ):
            return self.render_response(
                "update.html",
                current_post=current_post,
                error=error
            )

        return self.redirect_for("home")


class DeletePostHandler(BaseHandler):
    @authorize
    def post(self) -> HTTPResponse:
        """ Validates post id and user if everything is ok deletes post
            Then redirects to home page.
        
        Returns
        -------
        HTTPResponse
            Wheezy.http response object

        """
        post_id: str = str(self.route_args.get("post_id"))
        notes_controller = NotesController()

        if notes_controller.validate_post(
            post_id,
            Users.define_session(self.principal)
        ):
            notes_controller.delete_post(post_id)

        return self.redirect_for("home")
