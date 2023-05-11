#!/usr/bin/env python3

from app import app 
from models import db, User, Friend, Restaurant, SwipeInstance, SwipeSession


with app.app_context():

    Friend.query.delete()
    User.query.delete()
    Restaurant.query.delete()
    SwipeInstance.query.delete()
    SwipeSession.query.delete()

    user1=User(username="Example 1", type='user', email="t1@t.com", picture="", password_hash="test1")
    user2=User(username="Example 2",type='user', email="t2@t.com", picture="", password_hash="test2")
    user3=User(username="Example 3", type='user', email="t3@t.com", picture="", password_hash="test3")
    users=[user1,user2,user3]
    for u in users:
        db.session.add(u)
    db.session.commit()

    f1 = Friend(friend_one_id=user1.id, friend_two_id=user2.id, accepted=True)
    db.session.add(f1)
    db.session.commit()

    r1=Restaurant(name="Chilis",address="123 Main St", cuisine="American",picture="")
    r2=Restaurant(name="Applebees",address="456 Main St", cuisine="American",picture="")
    restaurants=[r1,r2]
    for r in restaurants:
        db.session.add(r)
    db.session.commit()

    ss=SwipeSession(connection_code='123')
    db.session.add(ss)
    db.session.commit()

    si1=SwipeInstance(user_id=user1.id, restaurant_id=r1.id, swipe_session_id=ss.id)
    si2=SwipeInstance(user_id=user2.id, restaurant_id=r2.id, swipe_session_id=ss.id)
    db.session.add(si1)
    db.session.add(si2)

    db.session.commit()

    