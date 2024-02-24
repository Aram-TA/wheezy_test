from data_base import db, CursorContextManager


def search_by_title_or_body(keyword: str) -> enumerate:
    """ Searches inside notes table from database, takes everything by
        keyword, returns it as enumerated list
    
    Parameters
    ----------
    keyword : str
        keyword from user input
    
    Returns
    -------
    enumerate
        enumerated list of search result

    """
    with CursorContextManager(db) as cursor:
        search_result = cursor.execute(
            '''
            SELECT * FROM notes WHERE (title LIKE ?1 OR body LIKE ?1)
            AND deleted = 0
            ''',
            (f"%{keyword}%",)
        ).fetchall()

    return enumerate(search_result, start=1)