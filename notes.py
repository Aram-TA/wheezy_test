from datetime import datetime
from dataBase import db


class NotesController:
    """
    Class that validates, creates, deletes, and updates notes/posts
    """
    __slots__ = ()

    def init_pages(self, page: int) -> tuple[list, int]:
        """ Defines pages count, content, current page for application

        Parameters
        ----------
        page : int

        Returns
        -------
        tuple[list, int]

        """
        cursor = db.cursor()
        all_posts: list = cursor.execute('SELECT * FROM notes').fetchall()

        posts_count: int = len(all_posts)
        items_per_page: int = 10

        start: int = (page - 1) * items_per_page
        end: int = start + items_per_page

        total_pages: int = (posts_count + items_per_page - 1) // \
            items_per_page if posts_count > 0 else 1

        items_on_page: list = all_posts[start:end]

        cursor.close()
        return items_on_page, total_pages

    def validate_post(
        self,
        post_id: str,
        user_session: None | dict = None
    ) -> dict | None:
        """ Validates post id for usage. Returns current post if id is valid

        Parameters
        ----------
        post_id : str
        read_mode : bool

        Returns
        -------
        dict | None

        """
        cursor = db.cursor()

        current_post: dict = cursor.execute(
            'SELECT * FROM notes WHERE id = ?',
            (post_id,)
        ).fetchone()

        cursor.close()

        if not current_post:
            print("I cant validate")
            return

        if user_session:
            if str(current_post["author_id"]) != user_session["user_id"]:
                return

        print("Everything is ok with validation")
        return current_post

    def delete_post(self, post_id: str) -> None | str:
        """ Deletes post by id form database

        Parameters
        ----------
        post_id : str

        """
        cursor = db.cursor()

        cursor.execute('DELETE FROM notes WHERE id = ?', (post_id,))

        cursor.close()
        db.commit()

    def update_post(
        self,
        post_id: str,
        title: str,
        body: str
    ) -> None | str:
        """ Updates post by id

        Parameters
        ----------
        post_id : str
        title : str
        body : str

        """
        if not title:
            return "Title is required."

        cursor = db.cursor()

        cursor.execute(
            'UPDATE notes SET title = ?, body= ? WHERE id = ?',
            (title, body, post_id)
        )

        cursor.close()
        db.commit()

    def create_post(
        self,
        title: str,
        body: str,
        user_session: dict
    ) -> None:
        """ Creates new post, assigns id to it by using

        Parameters
        ----------
        title : str
        body : str

        """
        cursor = db.cursor()

        cursor.execute(
            '''INSERT INTO notes (
                title,
                body,
                created,
                author_username,
                author_id
            )
            VALUES (?, ?, ?, ?, ?)''',
            (
                title,
                body,
                datetime.now().strftime("%Y-%m-%d %H:%M"),
                user_session['username'],
                user_session['user_id']
            )
        )

        cursor.close()
        db.commit()
