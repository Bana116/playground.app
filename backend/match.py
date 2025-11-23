from backend.models import Founder, Designer, Match, UserCredits
from backend.database import db
from backend.email_utils import send_match_email


# -----------------------------
# CREDIT SYSTEM HELPERS
# -----------------------------
def get_or_create_credits(user_type, user_id):
    credits = UserCredits.query.filter_by(user_type=user_type, user_id=user_id).first()
    if not credits:
        credits = UserCredits(user_type=user_type, user_id=user_id, credits=3)
        db.session.add(credits)
        db.session.commit()
    return credits


def can_match(user_type, user_id):
    return get_or_create_credits(user_type, user_id).credits > 0


def deduct_credit(user_type, user_id):
    credits = get_or_create_credits(user_type, user_id)
    credits.credits = max(0, credits.credits - 1)
    db.session.commit()


# ----------------------------------------------------
# SMART MATCHING SCORE (THE BRAINS)
# ----------------------------------------------------
def compute_match_score(founder, designer):
    score = 0

    # SCORE WEIGHTS
    WEIGHTS = {
        "design_need": 25,
        "niche": 20,
        "availability": 15,
        "tools": 10,
        "figma_level": 10,
        "hours": 10,
        "support": 10,
    }

    # ---- 1. MATCH DESIGN NEEDS → DESIGNER FOCUS ----
    founder_needs = founder.design_need.split(",")
    designer_focus = designer.focus.split(",")

    overlap = set(founder_needs) & set(designer_focus)
    score += len(overlap) / max(len(founder_needs), 1) * WEIGHTS["design_need"]

    # ---- 2. NICHE MATCH ----
    founder_niche = founder.niche.split(",")
    designer_niche = designer.niche.split(",")

    overlap = set(founder_niche) & set(designer_niche)
    score += len(overlap) / max(len(founder_niche), 1) * WEIGHTS["niche"]

    # ---- 3. AVAILABILITY ----
    founder_hours = founder.hours.lower()
    designer_avail = designer.availability.lower()
    if founder_hours in designer_avail:
        score += WEIGHTS["availability"]

    # ---- 4. TOOLS COMPATIBILITY ----
    founder_tools = founder.team_tools.lower()
    if founder_tools:
        for tool in designer.tools.split(","):
            if tool.lower() in founder_tools:
                score += WEIGHTS["tools"]
                break

    # ---- 5. FIGMA EXPERIENCE (if founder needs UI design) ----
    if "UI" in founder.design_need or "ui" in founder.design_need.lower():
        score += WEIGHTS["figma_level"] * (1 if "confident" in designer.figma_level.lower() else 0.5)

    # ---- 6. HOURS FIT ----
    if founder.hours.lower() in designer.availability.lower():
        score += WEIGHTS["hours"]

    # ---- 7. SUPPORT FIT ----
    if "feedback" in founder.support.lower() and "beginner" in designer.figma_level.lower():
        score += WEIGHTS["support"]

    return score


# ----------------------------------------------------
# FIND BEST DESIGNERS FOR A FOUNDER
# ----------------------------------------------------
def match_founder_to_designers(founder_id):
    founder = Founder.query.get(founder_id)
    if not founder:
        return []

    designers = Designer.query.all()
    if not designers:
        return []

    # compute scores
    scored = []
    for d in designers:
        score = compute_match_score(founder, d)
        scored.append((d, score))

    # sort high → low
    scored.sort(key=lambda x: x[1], reverse=True)

    # pick top 3
    top_designers = [d for d, s in scored[:3] if s > 0]

    results = []
    for d in top_designers:
        if not (can_match("founder", founder_id) and can_match("designer", d.id)):
            continue

        exists = Match.query.filter_by(founder_id=founder.id, designer_id=d.id).first()
        if exists:
            continue

        m = Match(founder_id=founder.id, designer_id=d.id)
        db.session.add(m)
        db.session.commit()

        deduct_credit("founder", founder.id)
        deduct_credit("designer", d.id)

        send_match_email(founder.email, d.email)

        results.append((founder, d))

    return results


# ----------------------------------------------------
# FIND BEST FOUNDER FOR A DESIGNER
# ----------------------------------------------------
def match_designer_to_founders(designer_id):
    designer = Designer.query.get(designer_id)
    if not designer:
        return []

    founders = Founder.query.all()
    if not founders:
        return []

    scored = []
    for f in founders:
        score = compute_match_score(f, designer)
        scored.append((f, score))

    scored.sort(key=lambda x: x[1], reverse=True)

    # designer gets 1 best match
    best = [f for f, s in scored[:1] if s > 0]

    results = []
    for f in best:
        if not (can_match("designer", designer_id) and can_match("founder", f.id)):
            continue

        exists = Match.query.filter_by(founder_id=f.id, designer_id=designer.id).first()
        if exists:
            continue

        m = Match(founder_id=f.id, designer_id=designer.id)
        db.session.add(m)
        db.session.commit()

        deduct_credit("designer", designer.id)
        deduct_credit("founder", f.id)

        send_match_email(f.email, designer.email)

        results.append((f, designer))

    return results
