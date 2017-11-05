from flask import Flask, make_response, redirect, render_template, redirect, url_for
from datacfg import DataCfg, get_cfg_list

app = Flask(__name__)
datacfg = get_cfg_list("cfg/list-num-tel.cfg")


@app.route('/')
def index():
    """ функция представления (view)"""
    return render_template("index.html", Title="Редактирование конфига",
                           Msg="Привет!", TekUsr=None)


@app.route('/add')
def add():
    return render_template("add.html")


@app.route('/edit/<num_tel>')
def edit(num_tel):
    return render_template("edit.html", datacfg=datacfg[num_tel])


@app.route('/del/<num_tel>')
def del_element(num_tel):
    if num_tel in datacfg:
        del datacfg[num_tel]
    # return redirect(url_for("view"))
    return render_template("del.html")


@app.route('/view')
def view():
    return render_template("view.html", datacfg=datacfg)


def run_app():
    print(len(datacfg))
    app.run(debug=True)


if __name__ == "__main__":
    run_app()
