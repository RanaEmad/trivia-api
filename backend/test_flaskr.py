import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format(
            'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    def test_get_categories(self):
        res = self.client().get('/categories')
        self.assertEqual(res.status_code, 200)

    def test_get_questions(self):
        res = self.client().get('/questions')
        self.assertEqual(res.status_code, 200)

    def test_delete_question(self):
        res = self.client().delete('/questions/5')
        self.assertEqual(res.status_code, 200)

    def test_delete_question_not_found(self):
        res = self.client().delete('/questions/1000')
        self.assertEqual(res.status_code, 404)

    def test_add_question(self):
        res = self.client().post('/questions',
                                 json={"question": "test question", "answer": "test answer", "difficulty": 1, "category": 1})
        self.assertEqual(res.status_code, 200)

    def test_search_question(self):
        res = self.client().post('/questions/search',
                                 json={"searchTerm": "What is the largest lake in Africa?"})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(data["questions"]), 1)

    def test_get_category_questions(self):
        res = self.client().get('/categories/2/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(data["questions"]), 4)

    def test_get_category_questions_not_found(self):
        res = self.client().get('/categories/2000/questions')
        self.assertEqual(res.status_code, 404)

    def test_get_quiz(self):
        res = self.client().post(
            '/quizzes', json={"previous_questions": [], "quiz_category": {"id": 2}})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["question"]["category"], 2)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
