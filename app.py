import json
import random

from flask import Flask, render_template, abort, request
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from flask_migrate import Migrate
from wtforms import StringField, SubmitField
from wtforms.validators import InputRequired, Length

from data import days


app = Flask(__name__)
SECRET_KEY = "my_super_secret_key"
app.config['SECRET_KEY'] = SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data/data_base.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)
migrate = Migrate(app, db)


teachers_goals_association = db.Table("teachers_goals",
                                      db.Column("teacher_id", db.Integer, db.ForeignKey("teachers.id")),
                                      db.Column("goal_id", db.Integer, db.ForeignKey("goals.id"))
                                      )


class Teacher(db.Model):
    __tablename__ = "teachers"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    about = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Float, nullable=False)
    picture = db.Column(db.String(), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    goals = db.relationship("Goal", secondary=teachers_goals_association, back_populates="teachers")
    free = db.Column(db.String(), nullable=False)

    bookings = db.relationship("Booking", back_populates="teacher")


class Booking(db.Model):
    __tablename__ = "bookings"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    phone = db.Column(db.String(), nullable=False)
    weekday = db.Column(db.String(), nullable=False)
    time = db.Column(db.String(), nullable=False)

    teacher_id = db.Column(db.Integer, db.ForeignKey("teachers.id"))
    teacher = db.relationship("Teacher", back_populates="bookings")


class Goal(db.Model):
    __tablename__ = "goals"

    id = db.Column(db.Integer, primary_key=True,)
    name = db.Column(db.String(), unique=True, nullable=False)
    value = db.Column(db.String(), nullable=False)
    teachers = db.relationship("Teacher", secondary=teachers_goals_association, back_populates="goals")
    requests = db.relationship("Request", back_populates="goal")


class Request(db.Model):
    __tablename__ = "requests"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    phone = db.Column(db.String(), nullable=False)
    time = db.Column(db.String(), nullable=False)
    goal_id = db.Column(db.Integer, db.ForeignKey("goals.id"))
    goal = db.relationship("Goal", back_populates="requests")


class RequestForm(FlaskForm):
    name = StringField("Вас зовут",
                       [InputRequired(message="Необходимо указать имя")])
    phone = StringField("Ваш телефон",
                        [InputRequired(message="Необходимо указать телефон"),
                         Length(min=7, max=15, message="Номер должен быть от 7 до 15-ти цифр")])
    submit = SubmitField('Найдите мне преподавателя')


class BookingForm(FlaskForm):
    name = StringField("Вас зовут",
                       validators=[InputRequired(message="Необходимо указать имя")])
    phone = StringField("Ваш телефон",
                        validators=[InputRequired(message="Необходимо указать телефон"),
                                    Length(min=7, max=15, message="Номер должен быть от 7 до 15-ти цифр")])
    submit = SubmitField('Записаться на пробный урок')


@app.errorhandler(404)
def render_not_found(error):
    """ 404 error custom handler """

    return 'Ничего не нашлось! Вот неудача, отправляйтесь на главную!\n<a href="/">TINYSTEPS</a>'


# done
@app.route('/')
def render_index():
    """ prepare data and render route '/' """

    teachers = db.session.query(Teacher).all()
    ch_teachers = random.sample(teachers, 6)
    goals = db.session.query(Goal).all()
    return render_template('index.html',
                           teachers=ch_teachers,
                           goals=goals)


@app.route('/all/', methods=['POST', 'GET'])
def render_all():
    """ prepare data and render route '/all/' """

    teachers = db.session.query(Teacher)
    selected_value = request.args.get('selected')
    if selected_value == '2':
        teachers = teachers.order_by(Teacher.rating.desc()).all()
    elif selected_value == '3':
        teachers = teachers.order_by(Teacher.price.desc()).all()
    elif selected_value == '4':
        teachers = teachers.order_by(Teacher.price).all()
    else:
        teachers = teachers.all()
        random.shuffle(teachers)
    return render_template('all.html',
                           teachers=teachers)


# done
@app.route('/goals/<goal>/')
def render_goal(goal):
    """ prepare data and render route for goal """

    teachers = db.session.query(Teacher).filter(Teacher.goals.any(Goal.name == goal)).order_by(Teacher.rating.desc())
    teachers = teachers.all()
    goal = db.session.query(Goal).filter(Goal.name == goal).first().value
    return render_template('goal.html',
                           goal=goal,
                           teachers=teachers)


# done
@app.route('/profiles/<int:teacher_id>/')
def render_teacher(teacher_id):
    """ prepare data and render route for teacher profile """

    teacher = db.session.query(Teacher).get_or_404(teacher_id)
    free = json.loads(teacher.free)
    return render_template('profile.html',
                           teacher=teacher,
                           free=free,
                           days=days)


# done
@app.route('/request/', methods=['GET', 'POST'])
def route_request():
    """ prepare data and render request route for both methods"""

    goals = db.session.query(Goal)
    first_goal = goals.first().name
    form = RequestForm()
    if request.method == "POST":
        if form.validate_on_submit():
            goal = request.form.get("goal")
            time = request.form.get("time")
            name = form.name.data
            phone = form.phone.data
            goal = db.session.query(Goal).filter(Goal.name == goal).first()
            req = Request(name=name, phone=phone, time=time, goal=goal)
            db.session.add(req)
            db.session.commit()
            return render_template('request_done.html',
                                   req=req)
    return render_template('request.html',
                           goals=goals.all(),
                           first_goal=first_goal,
                           form=form)


@app.route('/booking/<int:teacher_id>/<day>/<time>/', methods=['GET', 'POST'])
def route_booking(teacher_id, day, time):
    """ prepare data and render booking route for both methods"""

    form = BookingForm()
    time = time + ':00'
    teacher = db.session.query(Teacher).get_or_404(teacher_id)
    if day not in days:
        abort(404)
    if request.method == "POST":
        if form.validate_on_submit():
            name = form.name.data
            phone = form.phone.data
            free = json.loads(teacher.free)
            free[day][time] = False
            teacher.free = json.dumps(free)
            booking = Booking(name=name,
                              phone=phone,
                              weekday=day,
                              time=time,
                              teacher=teacher)
            db.session.add(booking)
            db.session.commit()
            day = days[day]
            return render_template('booking_done.html',
                                   day=day,
                                   booking=booking)
    return render_template('booking.html',
                           form=form,
                           teacher=teacher,
                           days=days,
                           day=day,
                           time=time)


if __name__ == '__main__':
    app.run()
