from wheezy.web import authorize
from wheezy.web.handlers import BaseHandler
# from flask import (
#     url_for,
#     request,
#     Response,
#     redirect,
#     Blueprint,
#     render_template,
# )

from searcher import Searcher
# from auth import login_required
from notes import NotesController

# bp = Blueprint("blog", __name__)


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
        if self.request.query:
            page = self.request.query.get("page", ["1"])[0]
            page = "1" if not page.isdigit() else page
        else:
            page = "1"

        page = int(page)

        items_on_page: list
        total_pages: int
        if self.principal:
            user_id, username = self.principal.id.split(",")
            user_session = {"user_id": user_id, "username": username}
        else:
            user_session = None

        items_on_page, total_pages = NotesController().init_pages(page)

        if page > total_pages or page < 1:
            return self.redirect_for("home", page=1)

        return self.render_response(
            "blog/home.html",
            items_on_page=items_on_page,
            total_pages=total_pages,
            page=page,
            user_session=user_session
        )


class SearchHandler(BaseHandler):
    def get(self):
        """ Renders search page.

        Returns
        -------
        Response

        """
        return self.render_response("blog/search.html", search_result=None)

    def post(self):
        """ Searches necessary data in posts database, renders what it found

        Returns
        -------
        Response

        """
        keyword: str = self.request.form["search_keyword"][0]
        search_result = Searcher().search_by_title_or_body(keyword)

        return self.render_response(
            "blog/search.html",
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
        current_post: dict | None

        if not (
            current_post := NotesController().validate_post(post_id)
        ):
            return self.redirect_for("home")

        return self.render_response(
            "blog/read-post.html",
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
        return self.render_response("blog/create.html", error=None)

    @authorize()
    def post(self):
        """ Does validations for post creating process then writes new data
        by using NotesController. Then redirects to index if everything is OK.

        Returns
        -------
        Response

        """
        title: str | None

        user_id, username = self.principal.id.split(",")
        user_session = {"user_id": user_id, "username": username}

        if not (title := self.request.form["title"][0]):
            return self.render_response(
                "blog/create.html",
                error="Title is required"
            )

        NotesController().create_post(
            title,
            self.request.form["body"][0],
            user_session
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
        post_id: str = str(self.route_args.get("post_id"))

        user_id, username = self.principal.id.split(",")
        user_session = {"user_id": user_id, "username": username}

        if not (
            current_post := NotesController().validate_post(
                post_id, user_session
            )
        ):
            return self.redirect_for("home")

        return self.render_response(
            "blog/update.html",
            current_post=current_post,
            error=None
        )

    @authorize
    def post(self):
        post_id: str = str(self.route_args.get("post_id"))
        notes_controller = NotesController()

        title: str = self.request.form["title"][0]
        current_post: dict | None

        user_id, username = self.principal.id.split(",")
        user_session = {"user_id": user_id, "username": username}

        if current_post := notes_controller.validate_post(
            post_id, user_session
        ):
            if (
                error := notes_controller.update_post(
                    post_id,
                    title,
                    self.request.form["body"][0]
                )
            ):
                return self.render_response(
                    "blog/update.html",
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
        user_id, username = self.principal.id.split(",")
        user_session = {"user_id": user_id, "username": username}

        post_id: str = str(self.route_args.get("post_id"))
        notes_controller = NotesController()

        if notes_controller.validate_post(post_id, user_session):
            notes_controller.delete_post(post_id)
        print("we are here inside delete handler")

        return self.redirect_for("home")
