""" Running file for whole WSGI application
"""
from wheezy.http import WSGIApplication
from wheezy.html.utils import html_escape
from wheezy.template.engine import Engine
from wheezy.template.loader import FileLoader
from wheezy.web.templates import WheezyTemplate
from wheezy.template.ext.core import CoreExtension
from wheezy.html.ext.template import WidgetExtension
from wheezy.web.middleware import (
    bootstrap_defaults,
    path_routing_middleware_factory
)

from urls import all_urls
from data_base import init_users_table, init_notes_table


def construct_app() -> WSGIApplication:
    """ Constructs wsgi application for our server with it's full configuration

    Returns
    -------
    WSGIApplication

    """
    engine = Engine(
        loader=FileLoader(["templates"]),
        extensions=[
            CoreExtension(),
            WidgetExtension(),
        ],
    )
    engine.global_vars.update({"h": html_escape})

    main = WSGIApplication(
        middleware=[
            bootstrap_defaults(url_mapping=all_urls),
            path_routing_middleware_factory,
        ],
        options={"render_template": WheezyTemplate(engine)},
    )
    return main


if __name__ == "__main__":
    from wsgiref.simple_server import make_server
    main = construct_app()
    try:
        init_notes_table()
        init_users_table()
        print("Visit http://localhost:8080/")
        make_server("", 8080, main).serve_forever()
    except KeyboardInterrupt:
        print("\nThanks!")
