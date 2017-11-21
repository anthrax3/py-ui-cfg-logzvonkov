from flask import Flask, make_response, redirect, render_template, request, flash, url_for, session, logging, \
    send_from_directory
# from datacfg import DataCfg, get_cfg_list, save_cfg_list
from wtforms import Form, StringField, SubmitField, TextAreaField, PasswordField, validators, DateField
from flask_sqlalchemy import SQLAlchemy, sqlalchemy  # pip install flask-sqlalchemy
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from py_log_zvonkov_pandas import run_log_zvonkov, del_file
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
app.config['UPLOAD_FOLDER'] = "result/"
# END инициализация БД и настроек
app.config.from_object(__name__)
db = SQLAlchemy(app)
# END конфигурирование приложение Flask
name_cfg_file = "cfg/list-num-tel.cfg"


# END конфигурирование приложение Flask


# классы форм

class RunForm(Form):
    """ форма ввода данных для запуска скрипта  """
    begin_date = DateField("Введите начальную дату (ГГГГ-ММ-ДД): ",
                           [validators.DataRequired()])  # format = '%Y-%m-%d %H:%M:%S')
    end_date = DateField("Введите начальную дату (ГГГГ-ММ-ДД): ",
                         [validators.DataRequired()])  # format = '%Y-%m-%d %H:%M:%S')
    submit = SubmitField("Register Now")


# END классы форм


# маршруты
@app.route('/')
def index():
    """ функция представления (view)"""
    return render_template("index.html", Title="Лог звонков (Казань)", Msg="Hello!")


@app.route('/about')
def about_page():
    return render_template("about.html")


@app.route('/run', methods=['GET', 'POST'])
def run():
    form = RunForm(request.form)
    if request.method == "POST" and form.validate():
        begin_date = request.form["begin_date"]
        end_date = request.form["end_date"]

        namefile = "logs-{} - {}.xlsx".format(begin_date, end_date)
        run_log_zvonkov(begin_date, end_date, app.config['UPLOAD_FOLDER'] + namefile, name_cfg_file)
        flash("Процесс запуска выгрузки завершен", "success")
        return redirect(url_for("download", filename=namefile))
    return render_template("run.html", form=form)


@app.route('/uploads/<filename>', methods=['GET', 'POST'])
def download(filename):
    uploads = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'])
    return send_from_directory(directory=uploads, filename=filename, as_attachment=True)


# END маршруты



def run_app():
    app.run(debug=True)


if __name__ == "__main__":
    run_app()
