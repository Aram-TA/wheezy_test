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


def construct_app():
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


'''
from flask import Flask

import blog
import auth
from dataBase import init_notes_table, init_users_table

def app_constructor(test_config: dict = {}) -> None:
    """
    configures flasks application object

    Parameters
    -----------
    test_config: dict

    Returns
    -------
    None

    """
    app = Flask(__name__)
    app.secret_key = "dev"

    if not test_config:
        app.config.from_pyfile("app_config.py", silent=True)
        # silent = if exists
    else:
        app.config.from_mapping(test_config)

    app.register_blueprint(auth.bp)
    app.register_blueprint(blog.bp)
    app.add_url_rule("/", endpoint="index")

    return app


if __name__ == "__main__":
    app = app_constructor()

    init_users_table(app)
    init_notes_table(app)

    app.run(debug=True)
'''
