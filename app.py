from flask import Flask, make_response, redirect, render_template, request, flash, url_for, session, logging
from datacfg import DataCfg, get_cfg_list
from wtforms import Form, StringField, SubmitField, TextAreaField, PasswordField, validators
from flask_sqlalchemy import SQLAlchemy, sqlalchemy  # pip install flask-sqlalchemy
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import os

# конфигурирование приложение Flask
name_db = 'data.sqlite'
basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SECRET_KEY'] = '7d441f27vfdred441f27567d441f2b617614872553bbca'
# инициализация БД и настроек
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + os.path.join(basedir, name_db)
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # ????
# END инициализация БД и настроек
app.config.from_object(__name__)
db = SQLAlchemy(app)
# END конфигурирование приложение Flask
datacfg = get_cfg_list("cfg/list-num-tel.cfg")


# END конфигурирование приложение Flask


def create_new_db(db):
    """ создание БД и заполнение таблицы ролей"""
    # создание таблиц
    db.create_all()
    # Добавление ролей
    admin_role = Role(name="Admin")
    user_role = Role(name="User")
    db.session.add(admin_role)
    db.session.add(user_role)
    db.session.commit()
    # END Добавление ролей


# модель БД для хранения учетных данных пользователей, имеющих права доступа к сервису
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


# END модель БД для хранения учетных данных пользователей, имеющих права доступа к сервису

#
user_role = Role(name="User")
admin_role = Role(name="Admin")


#

# классы форм
class EditForm(Form):
    num_tel = StringField("Номер телефона: ")
    fio_manager = StringField("ФИО МПП: ")
    fio_rg = StringField("ФИО РГ: ")
    plan_result_call = StringField("План результативных звонков в получасе: ")
    submit = SubmitField("Сохранить")


class RegisterForm(Form):
    """ форма регистрации пользователя  """
    name = StringField("Name", [validators.Length(min=5, max=50)])
    username = StringField("Username", [validators.Length(min=5, max=50)])
    email = StringField("Email", [validators.Length(min=6, max=50)])
    password = PasswordField("Password", [
        validators.DataRequired(),
        validators.EqualTo("confirm", message="Passwords do not match")
    ])
    confirm = PasswordField("Confirm Password")
    submit = SubmitField("Register Now")


# END классы форм


#  проверка если пользователь залогинен
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if "logged_in" in session:
            return f(*args, **kwargs)
        else:
            flash("Unauthorized. Please login", "error")
            return redirect(url_for("login"))

    return wrap

# проверка первый ли пользователь регистрируется? (первый зарегистрированный пользователь будет администратором(Admin),
# остальные регистрируются только администратором и остальные пользователи будут только с ролью обычных пользователей (User)
def is_administration(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if "logged_in" in session:
            if session["role"] == "Admin":
                return f(*args, **kwargs)
            else:
                flash("Please login as adminstrator for register new user", "error")
                return redirect(url_for("login"))
        else:
            if not os.path.exists(name_db):
                return f(*args, **kwargs)
            else:
                flash("Please login as adminstrator for register new user.", "error")
            return redirect(url_for("login"))

    return wrap



# маршруты
@app.route('/')
def index():
    """ функция представления (view)"""
    return render_template("index.html", Title="Редактирование конфига",
                           Msg="Hello!")


@app.route('/about')
def about_page():
    return render_template("about.html")


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = RegisterForm(request.form)
    if request.method == "POST":
        username = request.form["username"]
        password_user = request.form["password"]
        result = User.query.filter_by(username=username).first()
        if result is None:
            flash("Пользователь не найден или неверный пароль", "error")
        else:
            result_verify = result.verify_password(password_user)
            if result_verify:
                session["logged_in"] = True
                session["username"] = username
                session["role"] = result.role.name
                flash("Вы вошли, как {}".format(username), "success")
                return redirect(url_for("view"))
            else:
                flash("Пользователь не найден или неверный пароль", "error")
    return render_template("login.html", form=form)


@app.route("/logout", methods=['GET', 'POST'])
def logout():
    session.clear()
    flash("You are now logged out", "success")
    return redirect(url_for("login"))


@app.route("/register", methods=['GET', 'POST'])
@is_administration
def register():
    form = RegisterForm(request.form)
    if request.method == "POST" and form.validate():
        if not os.path.exists(name_db):
            create_new_db(db)
            role_new_user = "Admin"
        else:
            role_new_user = "User"
        name = request.form['name']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        user_new = User()
        user_new.name = name
        user_new.username = username
        user_new.email = email
        user_new.password = password
        user_new.role = Role.query.filter_by(name=role_new_user).first()
        db.session.add(user_new)
        db.session.commit()
        # TODO: сделать посик по талице User и проверить существует ли почта и имя порльзователя
        flash("You are registered and can log in", "success")
        return redirect(url_for("index"))
    return render_template("register.html", form=form)


@app.route('/add', methods=['GET', 'POST'])
@is_logged_in
def add():
    add_form = EditForm(request.form)
    if request.method == 'POST':
        # TODO: надо обработать если меняется номер телефона, надо удалить старый ключ и создать новую запись, если номер телефона не существует
        num_tel = str(request.form['num_tel'])
        if not (num_tel in datacfg):
            datacfg[num_tel] = DataCfg(request.form['fio_manager'], request.form['fio_rg'], num_tel,
                                       request.form['plan_result_call'])
        else:
            pass  # сделать предупреждение о том что такой номер есть
            return redirect(url_for('view'))
    return render_template("edit.html", form=add_form, title="Добавление нового МПП")


@app.route('/edit/<num_tel>', methods=['GET', 'POST'])
@is_logged_in
def edit(num_tel):
    edit_form = EditForm(request.form)
    # присваиваем данные в поля формы
    edit_form.fio_manager.data = datacfg[num_tel].fio_manager
    edit_form.fio_rg.data = datacfg[num_tel].fio_rg
    edit_form.num_tel.data = datacfg[num_tel].num_tel
    edit_form.plan_result_call.data = datacfg[num_tel].plan_result_call
    if request.method == 'POST':
        # TODO: надо обработать если меняется номер телефона, надо удалить старый ключ и создать новую запись, если номер телефона не существует
        # получаем данные из формы
        datacfg[num_tel].fio_manager = request.form['fio_manager']
        datacfg[num_tel].fio_rg = request.form['fio_rg']
        datacfg[num_tel].num_tel = request.form['num_tel']
        datacfg[num_tel].plan_result_call = request.form['plan_result_call']
        return redirect(url_for('view'))
    return render_template("edit.html", form=edit_form, title="Редактирование МПП")


@app.route('/del/<num_tel>')
@is_logged_in
def del_element(num_tel):
    if num_tel in datacfg:
        del datacfg[num_tel]
    return render_template("del.html")


@app.route('/view')
@is_logged_in
def view():
    return render_template("view.html", datacfg=datacfg)


# END маршруты



def run_app():
    app.run(debug=True)


if __name__ == "__main__":
    run_app()
