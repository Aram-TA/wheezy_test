from datetime import datetime

from data_base import db, CursorContextManager


def validate_post(
    post_id: str,
    user_session: None | dict = None
) -> dict | None:
    """ Validates post by id. If everything is ok returns it's data.
    
    Parameters
    ----------
    post_id : str
    user_session : None | dict, optional

    """
    with CursorContextManager(db) as cursor:

        current_post: dict = cursor.execute(
            'SELECT * FROM notes WHERE id = ?',
            (post_id,)
        ).fetchone()

    if not current_post:
        return

    if user_session and str(
            current_post["author_id"]) != user_session["user_id"]:
        return

    return current_post


def delete_post(post_id: str):
    """ Deletes post from database
    
    Parameters
    ----------
    post_id : str
        
    """
    with CursorContextManager(db) as cursor:
        cursor.execute('UPDATE notes SET deleted = 1 WHERE id = ?', (post_id,))

    db.commit()


def update_post(
    post_id: str,
    title: str,
    body: str
):
    """ Updates post by it's id and new data.
    
    Parameters
    ----------
    post_id : str
    title : str
        Title for updated version of post
    body : str
        Body for updated version of post

    """
    if not title:
        return "Title is required."

    with CursorContextManager(db) as cursor:
        cursor.execute(
            'UPDATE notes SET title = ?, body= ? WHERE id = ?',
            (title, body, post_id)
        )

    db.commit()


def create_post(
    title: str,
    user_session: dict,
    body: str = ""
) -> None:
    """ Creates new post then writes it to database
    
    Parameters
    ----------
    title : str
        title for new post
    user_session : dict
        Current user data from session
    body : str
        body for new post

    """
    with CursorContextManager(db) as cursor:
        cursor.execute(
            '''INSERT INTO notes (
                title,
                body,
                created,
                author_id
            )
            VALUES (?, ?, ?, ?)''',
            (
                title,
                body,
                datetime.now().strftime("%Y-%m-%d %H:%M"),
                int(user_session['user_id'])
            )
        )

    db.commit()
