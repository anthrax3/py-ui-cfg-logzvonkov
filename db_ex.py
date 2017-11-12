from flask import Flask, make_response, redirect, render_template, request, flash, url_for

from flask_sqlalchemy import SQLAlchemy   # pip install flask-sqlalchemy
import os

# инициализация БД и настроек
basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///"+os.path.join(basedir,'data.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # ????
db = SQLAlchemy(app)
# END инициализация БД и настроек

class Role(db.Model):
    __tablename__ = "roles"
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(64), unique = True)
    users = db.relationship("User",backref="role")   # отношения

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True,index=True)
    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"))  # связь с таблицей roles

    def __repr__(self):
        return "<User %r>" % self.username


# создание таблиц
db.create_all()

# удаление таблиц
# db.drop_all()

# вставка строк
admin_role = Role(name="Admin")
mod_role = Role(name="Moderator")
user_role = Role(name="User")
#
user_john = User(username="john", role=admin_role)
user_susan = User(username="susan", role=user_role)
user_david = User(username="david", role=user_role)
#
db.session.add(admin_role)
db.session.add_all([mod_role,user_role,user_david,user_john,user_susan])
#
db.session.commit()  # подтверждение изменений
#
# print(admin_role.id)


# изменение строк
# admin_role.name = "Администратор"
# db.session.add(admin_role)
# db.session.commit()


# извлечение строк
# print(User.query.all())
# print(User.query.filter_by(role=user_role).all())

