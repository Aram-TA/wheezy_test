from wheezy.web import authorize
from wheezy.http import HTTPResponse
from wheezy.web.handlers import BaseHandler
from wheezy.core.collections import first_item_adapter

from controllers.notes_controllers import (
    validate_post,
    create_post,
    update_post,
    delete_post
)
from controllers.users_controllers import define_session


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
            current_post := validate_post(post_id)
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

        create_post(
            title,
            define_session(self.principal),
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
            current_post := validate_post(
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
    def post(self) -> HTTPResponse:
        """ Validates post id and form that user passed. If everything is ok
            Updates post then returns to home page. Shows error inside
            update page if validation isn't passed. 
        
        Returns
        -------
        HTTPResponse
            Wheezy.http response object

        """
        adapted_form = first_item_adapter(self.request.form)
        post_id: str = str(self.route_args.get("post_id"))

        if (
            current_post := validate_post(
                post_id,
                define_session(self.principal)
                )
        ) and (
            error := update_post(
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

        if validate_post(
            post_id,
            define_session(self.principal)
        ):
            delete_post(post_id)

        return self.redirect_for("home")
