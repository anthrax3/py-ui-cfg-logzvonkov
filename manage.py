""" Добавляем поддержку обслуживающих проект скриптов: запуск dev-сервера,
миграции баз данных, cron-задачи и тому подобное"""
from flask_script import Manager, Shell
# from flask.ext.migrate import Migrate, MigrateCommand
from app import db
from app import app
from models import User, Role

# from models import *
# migrate = Migrate(app, db)

# Инициализируем менеджер
manager = Manager(app)


# Регистрируем команду, реализованную в виде потомка класса Command
# manager.add_command('db', MigrateCommand)


# регистрирует приложение, экземплятр БД и модели
def make_shell_context():
    return dict(db=db, User=User, Role=Role)


def make_create_new_dbsqlite():
    # удаление таблиц
    db.drop_all()
    # создание таблиц
    db.create_all()


manager.add_command("shell", Shell(make_context=make_shell_context))
# manager.add_command("newdb", make_create_new_dbsqlite)


if __name__ == '__main__':
    manager.run()
