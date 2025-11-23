from flask import Blueprint, render_template, request, redirect, url_for
from backend.email_utils import send_confirmation_email
from backend.database import db
from backend.models import Founder, Designer, Match, UserCredits
from backend.match import match_founder_to_designers, match_designer_to_founders
from backend.stripe_utils import create_checkout_session


main_bp = Blueprint("main", __name__)


# -------------------------
# PUBLIC PAGES
# -------------------------

@main_bp.get("/")
def home():
    return render_template("home.html")


@main_bp.get("/founder")
def founder_form():
    return render_template("founder_form.html")


@main_bp.get("/designer")
def designer_form():
    return render_template("designer_form.html")


# -------------------------
# FORM SUBMISSIONS
# -------------------------

@main_bp.post("/submit_founder")
def submit_founder():
    form = request.form

    founder = Founder(
        full_name=form.get("full_name"),
        email=form.get("email"),
        project_name=form.get("project_name"),
        website=form.get("website"),
        stage=",".join(form.getlist("stage")),
        design_need=",".join(form.getlist("design_need")),
        team_tools=form.get("team_tools"),
        paid=",".join(form.getlist("paid")),
        niche=",".join(form.getlist("niche")),
        hours=form.get("hours"),
        support=",".join(form.getlist("support")),
    )

    db.session.add(founder)
    db.session.commit()

    send_confirmation_email(founder.email, "Founder")

    return render_template("success.html", role="Founder", avatar="founder.png")


@main_bp.get("/founder_submitted")
def founder_submitted():
    return render_template("founder_submitted.html")


@main_bp.post("/submit_designer")
def submit_designer():
    form = request.form

    designer = Designer(
        full_name=form.get("full_name"),
        email=form.get("email"),
        availability=",".join(form.getlist("availability")),
        location=form.get("location"),
        portfolio=form.get("portfolio"),
        focus=",".join(form.getlist("focus")),
        interests=",".join(form.getlist("interest")),
        volunteer=",".join(form.getlist("volunteer")),
        niche=",".join(form.getlist("niche")),
        tools=",".join(form.getlist("tools")),
        figma_level=",".join(form.getlist("figma_level")),
        resources=",".join(form.getlist("resources")),
        extra=form.get("extra"),
    )

    db.session.add(designer)
    db.session.commit()

    send_confirmation_email(designer.email, "Designer")

    return render_template("success.html", role="Designer", avatar="designer.png")


@main_bp.get("/designer_submitted")
def designer_submitted():
    return render_template("designer_submitted.html")


# -------------------------
# MATCHING LOGIC ROUTES
# -------------------------

@main_bp.get("/match/founder/<int:id>")
def match_for_founder(id):
    results = match_founder_to_designers(id)

    if not results:
        return render_template("out_of_credits.html")

    founder, designer = results[0]   # show first match visually

    return render_template(
        "success.html",
        role="Designer",
        avatar="designer.png"
    )


@main_bp.get("/match/designer/<int:id>")
def match_for_designer(id):
    results = match_designer_to_founders(id)

    if not results:
        return render_template("out_of_credits.html")

    founder, designer = results[0]   # show first match visually

    return render_template(
        "success.html",
        role="Founder",
        avatar="founder.png"
    )


# -------------------------
# ADMIN MATCH VIEW
# -------------------------

@main_bp.get("/admin/matches")
def admin_matches():
    matches = Match.query.all()
    return render_template("admin_matches.html", matches=matches)


# -------------------------
# STRIPE PAYMENT ROUTES
# -------------------------

@main_bp.get("/buy_credits/<user_type>/<int:user_id>")
def buy_credits(user_type, user_id):
    checkout_url = create_checkout_session(user_type, user_id)
    return redirect(checkout_url)


@main_bp.get("/payment/success")
def payment_success():
    user_type = request.args.get("user_type")
    user_id = request.args.get("user_id")

    credits = UserCredits.query.filter_by(user_type=user_type, user_id=user_id).first()

    if credits:
        credits.credits += 5
    else:
        credits = UserCredits(user_type=user_type, user_id=user_id, credits=5)
        db.session.add(credits)

    db.session.commit()

    return render_template("payment_success.html")


@main_bp.get("/payment/cancel")
def payment_cancel():
    return render_template("payment_cancel.html")
