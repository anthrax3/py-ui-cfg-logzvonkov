from flask import Flask, make_response, redirect, render_template, request, flash, url_for
from datacfg import DataCfg, get_cfg_list

from wtforms import Form, StringField, SubmitField, validators


class EditForm(Form):
    num_tel = StringField("Номер телефона: ")
    fio_manager = StringField("ФИО МПП: ")
    fio_rg = StringField("ФИО РГ: ")
    plan_result_call = StringField("План результативных звонков в получасе: ")
    submit = SubmitField("Сохранить")


app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = '7d441f27vfdred441f27567d441f2b617614872553bbca'

datacfg = get_cfg_list("cfg/list-num-tel.cfg")
name_user = list()


@app.route('/')
def index():
    """ функция представления (view)"""
    return render_template("index.html", Title="Редактирование конфига",
                           Msg="Привет!", TekUsr=None)


@app.route('/add', methods=['GET', 'POST'])
def add():
    add_form = EditForm(request.form)
    if request.method == 'POST':
        # TODO: надо обработать если меняется номер телефона, надо удалить старый ключ и создать новую запись, если номер телефона не существует
        num_tel = str(request.form['num_tel'])
        if not (num_tel in datacfg):
            datacfg[num_tel] = DataCfg(request.form['fio_manager'], request.form['fio_rg'], num_tel,
                                       request.form['plan_result_call'])
            return redirect(url_for('view'))
    return render_template("edit.html", form=add_form, title="Добавление нового МПП")


@app.route('/edit/<num_tel>', methods=['GET', 'POST'])
def edit(num_tel):
    edit_form = EditForm(request.form)
    edit_form.fio_manager.data = datacfg[num_tel].fio_manager
    edit_form.fio_rg.data = datacfg[num_tel].fio_rg
    edit_form.num_tel.data = datacfg[num_tel].num_tel
    edit_form.plan_result_call.data = datacfg[num_tel].plan_result_call
    if request.method == 'POST':
        # TODO: надо обработать если меняется номер телефона, надо удалить старый ключ и создать новую запись, если номер телефона не существует
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


def run_app():
    print(len(datacfg))
    app.run(debug=True)


if __name__ == "__main__":
    run_app()
