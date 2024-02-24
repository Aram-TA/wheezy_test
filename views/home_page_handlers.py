from wheezy.web.handlers import BaseHandler
from wheezy.http import HTTPResponse

from controllers.users_controllers import define_session
from controllers.errors_controllers import render_http_error
from controllers.search_controllers import search_by_title_or_body
from controllers.pages_controllers import define_current_page, init_pages


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
        page: int = define_current_page(self.request.query)
        items_on_page, total_pages = init_pages(page)

        # TODO put here 404
        if page > total_pages or page < 1:
            return render_http_error(
                404,
                self.options,
                self.helpers
            )

        return self.render_response(
            "home.html",
            items_on_page=items_on_page,
            total_pages=total_pages,
            page=page,
            user_session=define_session(self.principal)
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
        search_result = search_by_title_or_body(keyword)

        return self.render_response(
            "search.html",
            search_result=search_result
        )
