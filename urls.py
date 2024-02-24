"""Summary

Attributes
----------
all_urls : list
    List of urls with their handlers for wsgi app
static_cache_profile : CacheProfile
    Wheezy.http CacheProfile object, defines caching headers for http
static_files : Any
    Static files for out application
"""

from wheezy.routing import url
from wheezy.http.cache import etag_md5crc32
from wheezy.web.handlers import file_handler
from wheezy.http import response_cache, CacheProfile
from wheezy.http.transforms import gzip_transform, response_transforms

from views.authentication_handlers import (
    RegisterHandler,
    LoginHandler,
    LogOutHandler
)
from views.home_page_handlers import (
    IndexHandler,
    HomeHandler,
    SearchHandler
)
from views.posts_handlers import (
    CreatePostHandler,
    UpdatePostHandler,
    DeletePostHandler,
    ReadPostHandler
)

static_cache_profile = CacheProfile(
    "public",
    duration=900,
    vary_environ=["HTTP_ACCEPT_ENCODING"],
    namespace="static",
    http_vary=["Accept-Encoding"],
    etag_func=etag_md5crc32,
    enabled=True
)

static_files = response_cache(static_cache_profile)(
    response_transforms(gzip_transform(compress_level=6))
    (file_handler(root="static/"))
)

all_urls = [
    url("", IndexHandler, name="index"),
    url("login", LoginHandler, name="login"),
    url("logout", LogOutHandler, name="logout"),
    url("search", SearchHandler, name="search"),
    url("register", RegisterHandler, name="register"),
    url("home", HomeHandler, {"page": 1}, name="home"),
    url("create_post", CreatePostHandler, name="crate_post"),
    url("read_post/{post_id:i}", ReadPostHandler, name="read_post"),
    url("delete_post/{post_id:i}", DeletePostHandler, name="delete_post"),
    url("update_post/{post_id:i}", UpdatePostHandler, name="update_post"),
    url("static/{path:any}", static_files, name="static"),
]
