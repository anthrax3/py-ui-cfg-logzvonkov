from flask import Flask, make_response, redirect, render_template, request, flash, url_for, session, logging
from datacfg import DataCfg, get_cfg_list
from wtforms import Form, StringField, SubmitField, TextAreaField, PasswordField, validators
from flask_sqlalchemy import SQLAlchemy,sqlalchemy  # pip install flask-sqlalchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os

# конфигурирование приложение Flask
basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SECRET_KEY'] = '7d441f27vfdred441f27567d441f2b617614872553bbca'
# инициализация БД и настроек
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # ????
# END инициализация БД и настроек
app.config.from_object(__name__)
db = SQLAlchemy(app)
# END конфигурирование приложение Flask
datacfg = get_cfg_list("cfg/list-num-tel.cfg")


# END конфигурирование приложение Flask


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

# маршруты
@app.route('/')
def index():
    """ функция представления (view)"""
    return render_template("index.html", Title="Редактирование конфига",
                           Msg="Привет!", TekUsr=None)


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == "POST" and form.validate():
        name = request.form['name']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        # role = user_role
        user_new = User()
        user_new.name=name
        user_new.username = username
        user_new.email=email
        user_new.password=password
        user_new.role=Role.query.filter_by(name="User").first()
        db.session.add(user_new)
        db.session.commit()
        # TODO: сделать посик по талице User и проверить существует ли почта и имя порльзователя
        return redirect(url_for("index"))
    return render_template("register.html", form=form)


@app.route('/add', methods=['GET', 'POST'])
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
def del_element(num_tel):
    if num_tel in datacfg:
        del datacfg[num_tel]
    return render_template("del.html")


@app.route('/view')
def view():
    return render_template("view.html", datacfg=datacfg)


# END маршруты

def run_app():
    app.run(debug=True)


if __name__ == "__main__":
    run_app()
