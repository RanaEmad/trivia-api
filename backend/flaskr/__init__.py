import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin
import random
import json

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
    CORS(app)
    cors = CORS(app, resources={r"/*": {"origins": "*"}})

    '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,PUT,POST,DELETE,OPTIONS')
        return response

    '''
  @TODO:
  Create an endpoint to handle GET requests
  for all available categories.
  '''
    @app.route("/categories")
    @cross_origin()
    def get_categories():
        categories = Category.query.all()
        formatted_categories = {}
        for category in categories:
            formatted_categories[category.id] = category.type
        response = {
            "success": True,
            "categories": formatted_categories
        }
        return jsonify(response)

    '''
  @TODO:
  Create an endpoint to handle GET requests for questions,
  including pagination (every 10 questions).
  This endpoint should return a list of questions,
  number of total questions, current category, categories.

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions.
  '''
    @app.route("/questions")
    @cross_origin()
    def get_questions():
        page = request.args.get("page", 1, type=int)
        start = (page - 1) * 10
        end = start + 10
        questions = Question.query.all()
        formatted_questions = [question.format() for question in questions]

        categories = Category.query.all()
        formatted_categories = {}
        for category in categories:
            formatted_categories[category.id] = category.type

        response = {
            "success": True,
            "questions": formatted_questions[start:end],
            "total_questions": len(formatted_questions),
            "categories": formatted_categories,
            "current_category": None
        }
        return jsonify(response)

    '''
  @TODO:
  Create an endpoint to DELETE question using a question ID.

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page.
  '''
    @app.route('/questions/<question_id>', methods=['DELETE'])
    @cross_origin()
    def delete_question(question_id):
        question = Question.query.filter_by(id=question_id).one_or_none()
        if question is None:
            abort(404)
        question.delete()
        response = {
            "success": True,
            "question_id": question_id
        }

        return jsonify(response)

    '''
  @TODO:
  Create an endpoint to POST a new question,
  which will require the question and answer text,
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab,
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.
  '''

    @app.route('/questions', methods=['POST'])
    @cross_origin()
    def add_question():
        question = Question(question=request.get_json()["question"], answer=request.get_json()[
                            "answer"], difficulty=request.get_json()["difficulty"], category=request.get_json()["category"])
        question.insert()
        response = {
            "success": True,
            "question_id": question.id
        }
        return jsonify(response)

    '''
  @TODO:
  Create a POST endpoint to get questions based on a search term.
  It should return any questions for whom the search term
  is a substring of the question.

  TEST: Search by any phrase. The questions list will update to include
  only question that include that string within their question.
  Try using the word "title" to start.
  '''
    @app.route("/questions/search", methods=['POST'])
    @cross_origin()
    def search_questions():
        search_term = request.get_json()["searchTerm"]
        page = request.args.get("page", 1, type=int)
        start = (page - 1) * 10
        end = start + 10
        questions = Question.query.filter(
            Question.question.ilike('%'+search_term+'%')).all()
        formatted_questions = [question.format() for question in questions]

        response = {
            "success": True,
            "questions": formatted_questions[start:end],
            "total_questions": len(formatted_questions),
            "current_category": None
        }
        return jsonify(response)

    '''
  @TODO:
  Create a GET endpoint to get questions based on category.

  TEST: In the "List" tab / main screen, clicking on one of the
  categories in the left column will cause only questions of that
  category to be shown.
  '''
    @app.route("/categories/<category_id>/questions")
    @cross_origin()
    def get_category_questions(category_id):
        category = Category.query.filter_by(id=category_id).one_or_none()
        if category is None:
            abort(404)
        page = request.args.get("page", 1, type=int)
        start = (page - 1) * 10
        end = start + 10
        questions = Question.query.filter_by(category=category_id).all()
        formatted_questions = [question.format() for question in questions]

        response = {
            "success": True,
            "questions": formatted_questions[start:end],
            "total_questions": len(formatted_questions),
            "current_category": category_id
        }
        return jsonify(response)

    '''
  @TODO:
  Create a POST endpoint to get questions to play the quiz.
  This endpoint should take category and previous question parameters
  and return a random questions within the given category,
  if provided, and that is not one of the previous questions.

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not.
  '''
    @app.route("/quizzes", methods=["POST"])
    @cross_origin()
    def get_quiz():
        previous_questions = request.get_json()["previous_questions"]
        quiz_category = request.get_json()["quiz_category"]

        question = {}
        if quiz_category["id"] != 0:
            quiz_category = request.get_json()["quiz_category"]
            question = Question.query.filter_by(category=quiz_category["id"]).filter(
                ~Question.id.in_(previous_questions)).first()
        else:
            question = Question.query.filter(
                ~Question.id.in_(previous_questions)).first()
        if question:
            question = question.format()
        response = {
            "success": True,
            "question": question
        }
        return jsonify(response)

    '''
  @TODO:
  Create error handlers for all expected errors
  including 404 and 422.
  '''
    @app.errorhandler(404)
    @cross_origin()
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "Not found"
        }), 404

    @app.errorhandler(422)
    @cross_origin()
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "Unprocessable"
        }), 422

    @app.errorhandler(500)
    @cross_origin()
    def internal_error(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "Internal Server Error"
        }), 500

    @app.errorhandler(400)
    @cross_origin()
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "Bad Request"
        }), 400

    return app
