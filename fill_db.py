import json

from data import days
from app import app, db, Teacher, Booking, Goal
from data import teachers, goals


def load_goals_to_db():
    for key, value in goals.items():
        goal = Goal(name=key, value=value)
        db.session.add(goal)
    db.session.commit()


def load_teachers_to_db():
    for teacher in teachers:
        #teacher_goals = json.dumps(teacher["goals"])
        free = json.dumps(teacher["free"])
        db_teacher = Teacher(id=teacher["id"],
                             name=teacher["name"],
                             about=teacher["about"],
                             rating=teacher["rating"],
                             picture=teacher["picture"],
                             price=teacher["price"],
                             #goals=teacher_goals,
                             free=free,
                             )
        db.session.add(db_teacher)
        for goal in teacher["goals"]:
            db_goal = db.session.query(Goal).filter(Goal.name == goal).first()
            db_teacher.goals.append(db_goal)
    db.session.commit()


if __name__ == "__main__":
    load_goals_to_db()
    load_teachers_to_db()

