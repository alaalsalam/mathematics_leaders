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
