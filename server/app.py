from flask import Flask, request, make_response, session
from flask_session import Session
from flask_migrate import Migrate
from flask_restful import Api, Resource
import requests
from models import User, Friend, Restaurant, SwipeInstance, SwipeSession
from flask_bcrypt import Bcrypt
from services import app,bcrypt,db
import os
from dotenv import load_dotenv
from datetime import timedelta


load_dotenv()

app.secret_key = os.environ.get('secretkey')

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)
api=Api(app)

class Logout(Resource):
    def get(self):
        try:
            session.pop('user_id')
            session.pop('user_type')
            return make_response({"message":"Logout successfull"},200)
        except Exception as e:
            return make_response({"message": [e.__str__()]}, 422)


class Login(Resource):
    def post(self):
        data=request.get_json()
        user=User.query.filter(User.email==data['email']).first()
        try:
            if user and user.authenticate(data['password']):
                session['user_id']=user.id
                session['user_type']=user.type
                return make_response({
                    "id":user.id,
                    "username":user.username, 
                    "type":user.type,
                }, 200)
            else: 
                return make_response({"message":"Login failed"},400)
        except Exception as e:
            return make_response({"message": [e.__str__()]}, 422)
    
    def get(self):
        user_id=session.get('user_id')
        try:
            if not user_id:
                return make_response({"message":"Unauthorized, not logged in."}, 401)
            user=User.query.filter(User.id==user_id).first()
            return make_response({
                "id":user.id,
                "username":user.username, 
                "type":user.type,
            },200)
        except Exception as e:
            return make_response({"message": [e.__str__()]}, 422)
    
    


class OneUsers(Resource):
    def get(self,id):
        user=User.query.filter(User.id==id).first()
        if not user:
            return make_response({'message':"User not found"}, 404)
        try:
            return make_response(user.to_dict())
        except Exception as e:
            return make_response({"message": [e.__str__()]}, 422)

    def patch(self,id):
        user=User.query.filter(User.id==id).first()
        if not user:
            return make_response({'message':"User not found"}, 404)
        try:
            data=request.get_json()
            for attr in data:
                setattr(user, attr, data[attr])
            db.session.add(user)
            db.session.commit()
            return make_response({'message':"Update successful"}, 200)
        except Exception as e:
            return make_response({"message": [e.__str__()]}, 422)
    
    def delete(self,id):
        user=User.query.filter(User.id==id).first()
        if not user:
            return make_response({'message':"User not found"}, 404)
        try:
            db.session.delete(user)
            db.session.commit()
            return make_response({'message':"Delete successful"},200)
        except Exception as e:
            return make_response({"message": [e.__str__()]}, 422)


class AllUsers(Resource):
    def get(self):
        try:
            users=User.query.all()
            users_dict=[u.to_dict() for u in users]
            return make_response(users_dict, 200)
        except Exception as e:
            return make_response({"message": [e.__str__()]}, 422)

    def post(self):
        data=request.get_json()
        exist_user=User.query.filter(User.username==data['username']).first()
        exist_email=User.query.filter(User.email==data['email']).first()
        if exist_email or exist_user:
            return make_response({"message":"Username or email already exist."},400)
        try:
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
            return make_response({'username':new_user.username, 'type':new_user.type}, 202)
        except Exception as e:
            return make_response({"message": [e.__str__()]}, 422)

class OneFriends(Resource):
    def patch(self, id):
        try:
            data=request.get_json()
            exist_combo1=Friend.query.filter(Friend.friend_one_id==data['user1'],Friend.friend_two_id==data["user2"]).first()
            exist_combo2=Friend.query.filter(Friend.friend_one_id==data["user2"], Friend.friend_two_id==data["user1"]).first()
            print(data)
            if exist_combo1: 
                for attr in data:
                    setattr(exist_combo1, attr, data[attr])
                db.session.add(exist_combo1)
                db.session.commit()
                return make_response({"message":"Success"})
            elif exist_combo2:
                for attr in data:
                    setattr(exist_combo2, attr, data[attr])
                db.session.add(exist_combo2)
                db.session.commit()
                return make_response({"message":"Success"})
            else: 
                return make_response({"message":"Something went wrong"})

        except Exception as e:
            return make_response({"message": [e.__str__()]}, 422)

    def delete(self,id):   
        try:
            data=request.get_json()
            exist_combo1=Friend.query.filter(Friend.friend_one_id==data['user1'],Friend.friend_two_id==data['user2']).first()
            exist_combo2=Friend.query.filter(Friend.friend_one_id==data['user2'], Friend.friend_two_id==data['user1']).first()
            if exist_combo1:
                db.session.delete(exist_combo1)
                db.session.commit()
                return make_response({'messsage':"Delete successful"})
            elif exist_combo2:
                db.session.delete(exist_combo2)
                db.session.commit()
                return make_response({'messsage':"Delete successful"})
            else:
                return make_response({'messsage':"Nothing to delete"})
        except Exception as e:
            return make_response({"message": [e.__str__()]}, 422)

class AllFriends(Resource):
    def get(self):
        try:
            
            friendships1=Friend.query.filter(Friend.friend_one_id==session['user_id']).all()
            friendships2=Friend.query.filter(Friend.friend_two_id==session['user_id']).all()
            allfriends=friendships1+friendships2
            f_dict=[f.to_dict() for f in allfriends]
            return make_response(f_dict, 200)
        except Exception as e:
            return make_response({"message": [e.__str__()]}, 422)
        
    def post(self):
        data=request.get_json()
        user1=User.query.filter(User.id==data['friend_one_id']).first()
        user2=User.query.filter(User.id==data['friend_two_id']).first()
        if user1==None or user2==None:
            return make_response({"message":"One or more users not found"},404)
        exist_combo1=Friend.query.filter(Friend.friend_one_id==user1.id,Friend.friend_two_id==user2.id).first()
        exist_combo2=Friend.query.filter(Friend.friend_one_id==user2.id, Friend.friend_two_id==user1.id).first()
        if exist_combo1 or exist_combo2:
            return make_response({"message":"Friendship already exists"},200)
        try:
            friendship=Friend(friend_one_id=user1.id, friend_two_id=user2.id)
            db.session.add(friendship)
            db.session.commit()
            return make_response(friendship.to_dict(), 202)
        except Exception as e:
            return make_response({"message": [e.__str__()]}, 422)


api.add_resource(Login, "/login")
api.add_resource(Logout, '/logout')
api.add_resource(OneUsers, '/users/<int:id>')
api.add_resource(AllUsers, '/users')
api.add_resource(OneFriends, '/friends/<int:id>')
api.add_resource(AllFriends, '/friends')




if __name__ == '__main__':
    app.run( port = 5555, debug = True )
