from flask import Flask, render_template
import flask_monitoringdashboard as dashboard
import sqlite3
from sqlite3 import Error
import os
from flask_bootstrap import Bootstrap
import jinja2


bootstrap = Bootstrap()


def create_db(db_file):
    try:
        conn = sqlite3.connect(db_file)
        print(sqlite3.version)
    except Error as e:
        print(e)
    finally:
        conn.close()


app = Flask(__name__)
my_loader = jinja2.ChoiceLoader([
    app.jinja_loader,
    jinja2.FileSystemLoader('templates/templates')
])
app.jinja_loader = my_loader

bootstrap.init_app(app)

dashboard.config.init_from(file='dashboard.cfg')
dashboard.bind(app)


@app.route('/')
def main():
    return render_template('index.html')


if __name__ == '__main__':
    if not os.path.exists('dashboard.db'):
        create_db('dashboard.db')
    else:
        pass
    app.run()

