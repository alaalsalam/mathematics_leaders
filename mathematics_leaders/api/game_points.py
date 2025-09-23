import frappe
from frappe import _

@frappe.whitelist(allow_guest=True)
def add_point(amount: int = 1):
    """يزيد challenge_points لمستخدم الجلسة في DocType: Game Users."""
    user = frappe.session.user
    # جلب username (حقل username في User قد يختلف عن user.name)
    username = frappe.db.get_value("User", user, "username") or user
    name = frappe.db.get_value("Game Users", {"username": username}, "name")
    if not name:
        frappe.throw(_("Game user not found for: {}").format(username))
    # الزيادة (مع افتراضي 0)
    current = frappe.db.get_value("Game Users", name, "challenge_points") or 0
    frappe.db.set_value("Game Users", name, "challenge_points", float(current) + float(amount))
    frappe.db.commit()
    return {"ok": True, "points": float(current) + float(amount)}


@frappe.whitelist(allow_guest=True)
def get_points():
    """أعد نقاط اللاعب ومعلومات بسيطة عن ترتيبه."""
    user = frappe.session.user
    if not user or user == "Guest":
        frappe.throw(_("You must be logged in to view your score."))

    username = frappe.db.get_value("User", user, "username") or user
    row = frappe.db.get_value(
        "Game Users",
        {"username": username},
        ["name", "challenge_points", "language", "profile_image"],
        as_dict=True,
    )
    if not row:
        frappe.throw(_("Game user not found for: {}").format(username))

    points = float(row.challenge_points or 0)
    total_players = frappe.db.count("Game Users") or 0
    higher_count = frappe.db.sql(
        """
        select count(*) from `tabGame Users`
        where ifnull(challenge_points, 0) > %(points)s
        """,
        {"points": points},
    )[0][0]
    rank = int(higher_count) + 1
    best = frappe.db.sql(
        "select max(ifnull(challenge_points,0)) from `tabGame Users`"
    )[0][0] or 0

    return {
        "ok": True,
        "points": points,
        "rank": rank,
        "players": total_players,
        "best": float(best),
        "username": username,
        "profile_image": row.profile_image,
        "game_user_name": row.name,
    }
