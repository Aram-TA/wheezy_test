from dataBase import db


class Searcher:
    def search_by_title_or_body(self, keyword: str):
        cursor = db.cursor()

        search_result = cursor.execute(
            'SELECT * FROM notes WHERE title LIKE ?1 OR body LIKE ?1',
            (f"%{keyword}%",)
        ).fetchall()

        cursor.close()
        return enumerate(search_result, start=1)
