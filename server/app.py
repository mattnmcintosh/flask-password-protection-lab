#!/usr/bin/env python3

from flask import request, session, make_response
from flask_restful import Resource

from config import app, db, api
from models import User, UserSchema


class Signup(Resource):

  def post(self):
    data = request.get_json() or {}
    try:
      new_user = User(username=data.get("username"),password_hash=data.get("password"),)
      db.session.add(new_user)
      db.session.commit()
      session["user_id"] = new_user.id
      return make_response(UserSchema().dump(new_user), 201)
    except Exception as e:
      db.session.rollback()
      return {"error": str(e)}, 400

class Login(Resource):

  def post(self):
    data = request.get_json() or {}
    user = User.query.filter_by(username=data.get("username")).first()

    if user and user.authenticate(data.get("password")):
      session["user_id"] = user.id
      return make_response(UserSchema().dump(user), 200)

    return {"message": "Invalid username or password"}, 401

class Logout(Resource):

  def delete(self):
    session["user_id"] = None
    return make_response("", 204)

class CheckSession(Resource):

  def get(self):
    user_id = session.get("user_id")
    if user_id:
      user = User.query.get(user_id)
      if user:
        return make_response(UserSchema().dump(user), 200)
    return make_response("", 204)

class ClearSession(Resource):

    def delete(self):
    
        session['page_views'] = None
        session['user_id'] = None

        return {}, 204

api.add_resource(ClearSession, '/clear', endpoint='clear')
api.add_resource(Signup, "/signup")
api.add_resource(Login, "/login")
api.add_resource(Logout, "/logout")
api.add_resource(CheckSession, "/check_session")

if __name__ == '__main__':
    app.run(port=5555, debug=True)
