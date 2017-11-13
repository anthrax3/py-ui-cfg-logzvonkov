from flask import Flask, make_response, redirect, render_template, request, flash, url_for
import os
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy  # pip install flask-sqlalchemy

# инициализация БД и настроек
basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # ????
db = SQLAlchemy(app)


# END инициализация БД и настроек

class Role(db.Model):
    __tablename__ = "roles"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship("User", backref="role")  # отношения


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    username = db.Column(db.String(50), unique=True, index=True)
    email = db.Column(db.String(50), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"))  # связь с таблицей roles
    password_hash = db.Column(db.String(256))  # храним хэш пароля

    def __repr__(self):
        return "<User %r>" % self.username

    @property
    def password(self):
        raise AttributeError("password is not readable attribute")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)


if __name__ == "__main__":
    # user_role = Role(name="User")
    # admin_role = Role(name="Admin")
    # roles = Role.query.filter_by(name="User").first()
    #
    # print("Результат:",roles.id)

    # удаление таблиц
    db.drop_all()
    # создание таблиц
    db.create_all()
    # Добавление ролей
    admin_role = Role(name="Admin")
    user_role = Role(name="User")
    db.session.add(admin_role)
    db.session.add(user_role)
    db.session.commit()
    # END Добавление ролей
    print("Done")





# вставка строк
# admin_role = Role(name="Admin")
# user_role = Role(name="User")
# db.session.add(admin_role)
# db.session.add(user_role)
# db.session.commit()
# #
# user_john = User(username="john", role=admin_role)
# user_susan = User(username="susan", role=user_role)
# user_david = User(username="david", role=user_role)
# #
# db.session.add(admin_role)
# db.session.add_all([mod_role,user_role,user_david,user_john,user_susan])
# #
# db.session.commit()  # подтверждение изменений
#
# print(admin_role.id)


# изменение строк
# admin_role.name = "Администратор"
# db.session.add(admin_role)
# db.session.commit()


# извлечение строк
# print(User.query.all())
# print(User.query.filter_by(role=user_role).all())
