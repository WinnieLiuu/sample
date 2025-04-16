# flask_app/models.py
from . import db

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f"<User {self.account}>"
    
class Missions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    missionId = db.Column(db.String(100), nullable=False)
    missionName = db.Column(db.String(100), nullable=False)
    robot = db.Column(db.String(50), nullable=False)
    missionStatus = db.Column(db.String(50), nullable=False)
    startTime = db.Column(db.String(50), nullable=False)
    finishTime = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f"<Missions {self.missionId}>"