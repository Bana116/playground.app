from backend.database import db
from datetime import datetime

class Founder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120))
    email = db.Column(db.String(120))
    project_name = db.Column(db.String(255))
    website = db.Column(db.String(255))
    stage = db.Column(db.Text)
    design_need = db.Column(db.Text)
    team_tools = db.Column(db.String(255))
    paid = db.Column(db.Text)
    niche = db.Column(db.Text)
    hours = db.Column(db.String(50))
    support = db.Column(db.Text)


class Designer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120))
    email = db.Column(db.String(120))
    availability = db.Column(db.Text)
    location = db.Column(db.String(120))
    portfolio = db.Column(db.String(255))
    focus = db.Column(db.Text)
    interests = db.Column(db.Text)
    volunteer = db.Column(db.Text)
    niche = db.Column(db.Text)
    tools = db.Column(db.Text)
    figma_level = db.Column(db.Text)
    resources = db.Column(db.Text)
    extra = db.Column(db.Text)


class Match(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    founder_id = db.Column(db.Integer, db.ForeignKey("founder.id"))
    designer_id = db.Column(db.Integer, db.ForeignKey("designer.id"))

    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    founder = db.relationship("Founder", backref="matches")
    designer = db.relationship("Designer", backref="matches")


class UserCredits(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_type = db.Column(db.String(50))   # “founder” or “designer”
    user_id = db.Column(db.Integer)        # maps to Founder.id or Designer.id
    credits = db.Column(db.Integer, default=3)
