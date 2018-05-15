from flask import Flask
import os
from flask_sqlalchemy import SQLAlchemy
from random import random, randint


basedir = os.path.abspath(os.path.dirname(__file__))


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.db')
app.config['SLOW_QUERY_TIME'] = 0.0001
app.config['SQLALCHEMY_RECORD_QUERIES'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
from main import main as main_blueprint
app.register_blueprint(main_blueprint, url_prefix='/')


class Data(db.Model):
    __tablename__ = 'data'
    id = db.Column(db.Integer, primary_key=True)
    temp = db.Column(db.Float)
    humd = db.Column(db.Float)


def generate_fake_data(num=10000):
    for i in range(num):
        fake_data = Data(temp=randint(-50, 50)+round(random(),2),
                        humd=randint(0, 100)+round(random(),2))
        try:
            db.session.add(fake_data)
            db.session.commit()
        except Exception:
            db.session.rollback()
            db.session.flush()


if __name__ == '__main__':
    db.create_all()
    # generate_fake_data()
    if not os.path.exists('app.db'):
        generate_fake_data()
    else:
        pass
    app.run(debug=True)
