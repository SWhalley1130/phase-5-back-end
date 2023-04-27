from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy

from sqlalchemy.ext.hybrid import hybrid_property
from services import bcrypt,db

class User(db.Model, SerializerMixin):
    __tablename__="users"

    serialize_rules=('-friendships.users_f_backref', '-swipe_instances.users_si_backref',)

    id=db.Column(db.Integer, primary_key=True)
    username=db.Column(db.String, unique=True)
    type=db.Column(db.String)
    picture=db.Column(db.String)
    _password_hash=db.Column(db.String)
    email=db.Column(db.String, unique=True, nullable=False)    
    friendships=db.relationship("Friend", foreign_keys="[Friend.friend_one_id]", backref='users_f_backref', cascade = "all,delete,delete-orphan")
    swipe_instances=db.relationship("SwipeInstance", backref='users_si_backref', cascade = "all,delete,delete-orphan" )


    @hybrid_property
    def hash_password(self):
        return self._password_hash


    @hash_password.setter
    def password_hash(self, password):
        password_hash=bcrypt.generate_password_hash(password.encode('utf-8'))
        self._password_hash=password_hash.decode('utf-8')

    @hybrid_property
    def hash_password(self):
        return self._password_hash
    
    def authenticate(self, password):
        return bcrypt.check_password_hash(self.password_hash, password.encode('utf-8'))
    
class Friend(db.Model, SerializerMixin):
    __tablename__='friends'

    serialize_rules=('-users_f_backref',)

    id=db.Column(db.Integer, primary_key=True)
    friend_one_id=db.Column(db.Integer, db.ForeignKey('users.id'))
    friend_two_id=db.Column(db.Integer, db.ForeignKey('users.id'))

class Restaurant(db.Model, SerializerMixin):
    __tablename__='restaurants'

    serializerules=('-swipe_instances.restaurants_si_backref',)

    id=db.Column(db.Integer, primary_key=True)
    address=db.Column(db.String)
    cuisine=db.Column(db.String)
    picture=db.Column(db.String)
    swipe_instances=db.relationship("SwipeInstance", backref='restaurants_si_backref', cascade = "all,delete,delete-orphan" )

class SwipeInstance(db.Model, SerializerMixin):
    __tablename__='swipe_instances'

    serialize_rules=('-users_si_backref', "-restaurants_si_backref",'-swipe_sessions_si_backref',)

    id=db.Column(db.Integer, primary_key=True)
    user_id=db.Column(db.Integer, db.ForeignKey('users.id'))
    restaurant_id=db.Column(db.Integer, db.ForeignKey('restaurants.id'))
    swipe_session_id=db.Column(db.Integer, db.ForeignKey('swipe_sessions.id'))


class SwipeSessions(db.Model, SerializerMixin):
    __tablename__='swipe_sessions'

    serializerules=('-swipe_instances.swipe_sessions_si_backref',)

    id=db.Column(db.Integer, primary_key=True)
    connection_code=db.Column(db.String, unique=True)
    swipe_instances=db.relationship('SwipeInstance', backref='swipe_sessions_si_backref', cascade="all,delete,delete-orphan" )



    


