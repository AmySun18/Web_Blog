import uuid
from src.common.database import Database
from flask import session
from src.models.blog import Blog
import datetime


class User(object):
    pass

    def __init__(self, email, password, _id=None):
        self.email = email
        self.password = password
        self._id = uuid.uuid4().hex if _id is None else _id

    @classmethod
    def get_by_email(cls, email):
        user = Database.find_one(collection='users', query={'email': email})
        if user is not None:
            return cls(**user)

    @classmethod
    def get_by_id(cls, id):
        user = Database.find_one(collection='users', query={'_id': id})
        if user is not None:
            return cls(**user)

    @staticmethod
    def login_valid(email, password):
        user = User.get_by_email(email)
        if user is not None:
            return user.password == password
        else:
            return False

    @classmethod
    def register(cls, email, password):
        user = cls.get_by_email(email)
        if user is None:
            new_user = cls(email, password)
            new_user.save_to_mongo()
            session['email'] = email
            return True
        else:
            return False

    @staticmethod
    def login(user_email):
        # login_valid has already been called
        # Record the email information in the session
        session['email'] = user_email

    @staticmethod
    def logout():
        session['email'] = None

    def get_blogs(self):
        return Blog.get_from_author_id(self._id)

    def new_blog(self, title, description):
        blog = Blog(author=self.email,
                    title=title,
                    description=description,
                    author_id=self._id)
        blog.save_to_mongo()

    def new_post(self, blog_id, title, content, date=datetime.datetime.utcnow()):
        blog = Blog.from_mongo(blog_id)
        blog.new_post(title=title,
                      content=content,
                      date=date)

    def json(self):
        return {
            "email": self.email,
            "_id": self._id,
            "password": self.password ## Not safe
        }

    def save_to_mongo(self):
        Database.insert("users", self.json())
