from wheezy.http import HTTPResponse


def render_http_error(
    status_code: int,
    options: dict,
    helpers: dict
) -> HTTPResponse:
    """ Renders http error page from templates by given status code

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
