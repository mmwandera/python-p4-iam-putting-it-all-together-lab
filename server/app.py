#!/usr/bin/env python3

from flask import request, session
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe

# If the user's username and password are not authenticated: Return a JSON response with an error message, and a status of 401 (Unauthorized).
# If the user is not logged in when they make the request: Return a JSON response with an error message, and a status of 401 (Unauthorized).

@app.before_request
def check_if_logged_in():
    open_access_list = [
        'signup',
        'login',
        'check_session'
    ]

    if (request.endpoint) not in open_access_list and (not session.get('user_id')):
        return {'error': '401 Unauthorized'}, 401


# SIGN UP FEATURE:
# Handle sign up by implementing a POST /signup route. It should:
class Signup(Resource):
    
    # Be handled in a Signup resource with a post() method.
    # In the post() method, if the user is valid:
    def post(self):

        # In the post() method, if the user is valid:
        request_json = request.get_json()

        username = request_json.get('username')
        password = request_json.get('password')
        image_url = request_json.get('image_url')
        bio = request_json.get('bio')

        # Save a new user to the database with their username, encrypted password, image URL, and bio.
        user = User(
            username=username,
            image_url=image_url,
            bio=bio
        )

        # the setter will encrypt this
        user.password_hash = password

        try:

            db.session.add(user)
            db.session.commit()

            # Save the user's ID in the session object as user_id.
            session['user_id'] = user.id

            # Return a JSON response with the user's ID, username, image URL, and bio; and an HTTP status code of 201 (Created).
            return user.to_dict(), 201

        # If the user is not valid: Return a JSON response with the error message, and an HTTP status code of 422 (Unprocessable Entity).
        except IntegrityError:

            return {'error': '422 Unprocessable Entity'}, 422


# AUTO-LOGIN FEATURE:
# Handle auto-login by implementing a GET /check_session route. It should:
class CheckSession(Resource):

    # Be handled in a CheckSession resource with a get() method.
    def get(self):
        
        # In the get() method, if the user is logged in (if their user_id is in the session object):
        user_id = session['user_id']
        if user_id:
            user = User.query.filter(User.id == user_id).first()
            # Return a JSON response with the user's ID, username, image URL, and bio; and an HTTP status code of 200 (Success).
            return user.to_dict(), 200
        
        # If the user is not logged in when they make the request: Return a JSON response with an error message, and a status of 401 (Unauthorized).
        return {}, 401


# LOGIN FEATURE:
# Handle login by implementing a POST /login route. It should:
class Login(Resource):
    
    # Be handled in a Login resource with a post() method.
    def post(self):

        request_json = request.get_json()

        username = request_json.get('username')
        password = request_json.get('password')

        user = User.query.filter(User.username == username).first()

        # In the post() method, if the user's username and password are authenticated:
        if user:
            if user.authenticate(password):

                # Save the user's ID in the session object.
                session['user_id'] = user.id
                # Return a JSON response with the user's ID, username, image URL, and bio.
                return user.to_dict(), 200

        # If the user's username and password are not authenticated: Return a JSON response with an error message, and a status of 401 (Unauthorized).  
        return {'error': '401 Unauthorized'}, 401


# LOGOUT FEATURE:
# Handle logout by implementing a DELETE /logout route. It should:
class Logout(Resource):

    # Be handled in a Logout resource with a delete() method.
    # In the delete() method, if the user is logged in (if their user_id is in the session object):
    def delete(self):

        # Remove the user's ID from the session object.
        session['user_id'] = None
        # Return an empty response with an HTTP status code of 204 (No Content).
        return {}, 204
        


# RECIPES FEATURE:
# Handle recipe viewing by implementing a GET /recipes route. It should:
class RecipeIndex(Resource):

    # RECIPE LIST FEATURE:
    # Be handled in a RecipeIndex resource with a get() method
    def get(self):

        # In the get() method, if the user is logged in (if their user_id is in the session object):
        user = User.query.filter(User.id == session['user_id']).first()
        # Return a JSON response with an array of all recipes with their title, instructions, and minutes to complete data along with a nested user object; and an HTTP status code of 200 (Success).
        return [recipe.to_dict() for recipe in user.recipes], 200
        
    # RECIPE CREATION FEATURE:
    # Handle recipe creation by implementing a POST /recipes route. It should: 
    # Be handled in the RecipeIndex resource with a post() method.
    def post(self):

        request_json = request.get_json()

        title = request_json['title']
        instructions = request_json['instructions']
        minutes_to_complete = request_json['minutes_to_complete']

        # In the post() method, if the user is logged in (if their user_id is in the session object):
        try:

            recipe = Recipe(
                title=title,
                instructions=instructions,
                minutes_to_complete=minutes_to_complete,
                user_id=session['user_id'],
            )

            # Save a new recipe to the database if it is valid. The recipe should belong to the logged in user, and should have title, instructions, and minutes to complete data provided from the request JSON.
            db.session.add(recipe)
            db.session.commit()

            # Return a JSON response with the title, instructions, and minutes to complete data along with a nested user object; and an HTTP status code of 201 (Created).
            return recipe.to_dict(), 201

        # If the recipe is not valid:
        except IntegrityError:
            # Return a JSON response with the error messages, and an HTTP status code of 422 (Unprocessable Entity).
            return {'error': '422 Unprocessable Entity'}, 422


api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)