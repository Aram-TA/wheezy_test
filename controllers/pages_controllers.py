from data_base import db, CursorContextManager


def init_pages(page: int) -> tuple[list, int]:
    """Summary

    Parameters
    ----------
    page : int
        Current page for user

    Returns
    -------
    tuple[list, int]
        items_on_page, total_pages

    """
    with CursorContextManager(db) as cursor:

        limit: int = 2
        offset: int = (page - 1) * limit

        items_on_page: list = cursor.execute(
            '''
            SELECT notes.id, notes.author_id, notes.title, notes.body,
            notes.created, users.username as creator
            FROM notes INNER JOIN users ON notes.author_id = users.id
            WHERE deleted = 0
            LIMIT ? OFFSET ?
            ''',
            (limit, offset)
        ).fetchall()

        posts_count: int = len(
            [post for post in cursor.execute('SELECT id FROM notes')]
        )
        total_pages = ((posts_count + limit - 1) // limit) - 1 if posts_count \
            else 1

    return items_on_page, total_pages


def define_current_page(query: dict) -> int:
    """ Validation for query string inside url. If it fails it returns 0

    Parameters
    ----------
    query : str
        Query string from user request

    Returns
    -------
    int

    """
    try:
        page = int(query.get("page", ["1"])[0])
        return page if page < 10000 else 0
    except ValueError:
        return 0
