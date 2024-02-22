from wheezy.web import authorize
from wheezy.web.handlers import BaseHandler
from wheezy.security import Principal

from controllers import (
    define_session,
    define_current_page,
    Searcher,
    NotesController,
    Users,
    init_pages
)


class RegisterHandler(BaseHandler):
    def get(self):
        """ Renders register template

        Returns
        -------
        Response

        """
        return self.render_response("register.html", error=None)

    def post(self):
        """ Does some validation for registration
        then if it succeed redirects to login

        Returns
        -------
        Response

        """
        users = Users()

        if error := users.validate_registration(self.request.form):
            return self.render_response("register.html", error=error)

        users.reg_new_acc(self.request.form)

        return self.redirect_for("login")


class LoginHandler(BaseHandler):
    def get(self):
        """ Renders login template

        Returns
        -------
        Response

        """
        return self.render_response("login.html", error=None)

    def post(self):
        """ Does some validation for login then if it succeed redirects
        to index page. Also handles current session of logged in user

        Returns
        -------
        Response

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
    def get(self):
        """ Clears all data of current flask
        session and redirects to index page

        Returns
        -------
        Response

        """
        del self.principal
        return self.redirect_for("home")


class IndexHandler(BaseHandler):
    def get(self):
        return self.redirect_for("home")


class HomeHandler(BaseHandler):
    def get(self):
        """ Returns rendered home template when client goes to "/" url

        Returns
        -------
        Response

        """
        page: int = define_current_page(self.request.query)
        items_on_page, total_pages = init_pages(page)

        # TODO put here 404
        if page > total_pages:
            return self.redirect_for("home", page=1)

        return self.render_response(
            "home.html",
            items_on_page=items_on_page,
            total_pages=total_pages,
            page=page,
            user_session=define_session(self.principal)
        )


class SearchHandler(BaseHandler):
    def get(self):
        """ Renders search page.

        Returns
        -------
        Response

        """
        return self.render_response("search.html", search_result=None)

    def post(self):
        """ Searches necessary data in posts database, renders what it found

        Returns
        -------
        Response

        """
        keyword: str = self.request.form["search_keyword"][0]
        search_result = Searcher().search_by_title_or_body(keyword)

        return self.render_response(
            "search.html",
            search_result=search_result
        )


class ReadPostHandler(BaseHandler):
    def get(self):
        """ Renders special page for current post reading.

        Parameters
        ----------
        post_id : str

        Returns
        -------
        Response

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
    def get(self):
        """ Renders post creating html for our server.

        Returns
        -------
        Response

        """
        return self.render_response("create.html", error=None)

    @authorize()
    def post(self):
        """ Does validations for post creating process then writes new data
        by using NotesController. Then redirects to index if everything is OK.

        Returns
        -------
        Response

        """
        if not (title := self.request.form["title"][0]):
            return self.render_response(
                "create.html",
                error="Title is required"
            )

        NotesController().create_post(
            title,
            self.request.form["body"][0],
            define_session(self.principal)
        )

        return self.redirect_for("home")


class UpdatePostHandler(BaseHandler):
    @authorize
    def get(self):
        """
        Renders page for post updating for user, if validation is ok. If not
        redirects to index page

        Parameters
        -----------
        post_id: str

        Returns
        -------
        Response

        """
        if not (
            current_post := NotesController().validate_post(
                str(self.route_args.get("post_id")),
                define_session(self.principal)
            )
        ):
            return self.redirect_for("home")

        return self.render_response(
            "update.html",
            current_post=current_post,
            error=None
        )

    @authorize
    def post(self):
        notes_controller = NotesController()

        post_id: str = str(self.route_args.get("post_id"))

        if (
            current_post := notes_controller.validate_post(
                post_id,
                define_session(self.principal)
                )
        ) and (
            error := notes_controller.update_post(
                post_id,
                self.request.form["title"][0],
                self.request.form["body"][0]
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
    def post(self):
        """ Deletes post by post_id

        Parameters
        -----------
        post_id: str

        Returns
        -------
        Response

        """
        post_id: str = str(self.route_args.get("post_id"))
        notes_controller = NotesController()

        if notes_controller.validate_post(
            post_id,
            define_session(self.principal)
        ):
            notes_controller.delete_post(post_id)

        return self.redirect_for("home")
