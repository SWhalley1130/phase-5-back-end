from flask import Flask, request, make_response, jsonify, session
from flask_session import Session
from flask_migrate import Migrate
from flask_restful import Api, Resource
import requests
from models import User, Friend, Restaurant, SwipeInstance, SwipeSessions
from flask_bcrypt import Bcrypt
from services import bcrypt,db
import os
from dotenv import load_dotenv
from datetime import timedelta


load_dotenv()

app=Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY_S')

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)
api=Api(app)

class OneUsers(Resource):
    def get(self,id):
        pass
    def patch(self,id):
        pass
    def delete(self,id):
        pass

class AllUsers(Resource):
    def get(self):
        users=User.query.all()
        users_dict=[u.to_dict() for u in users]
        return make_response(users_dict, 200)

    def post(self):
        data=request.get_json()
        new_user=User(
            username=data['username'],
            email=data['email'],
            type=data['type']
        )
        new_user.password_hash=data['password']
        db.session.add(new_user)
        db.session.commit()
        session['user_id']=new_user.id
        session['user_type']=new_user.type
        return make_response(new_user.to_dict(), 202)

        

api.add_resource(OneUsers, '/users/<int:id>')
api.add_resource(AllUsers, '/users')




if __name__ == '__main__':
    #print(os.urandom(24))
    app.run( port = 5555, debug = True )
