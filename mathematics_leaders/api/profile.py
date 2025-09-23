import frappe
from frappe import _
from frappe.utils.password import update_password
from frappe.auth import LoginManager


def _get_game_user_doc(username: str):
    name = frappe.db.get_value("Game Users", {"username": username}, "name")
    if not name:
        frappe.throw(_("Game user not found for: {}").format(username))
    return name


@frappe.whitelist()
def set_profile_image(file_url: str):
    if not file_url:
        frappe.throw(_("File URL is required."))
    user = frappe.session.user
    if not user or user == "Guest":
        frappe.throw(_("You must be logged in."))

    username = frappe.db.get_value("User", user, "username") or user
    docname = _get_game_user_doc(username)
    frappe.db.set_value("Game Users", docname, "profile_image", file_url)
    frappe.db.commit()
    return {"ok": True, "profile_image": file_url}


@frappe.whitelist()
def verify_current_password(current_password: str):
    current_password = (current_password or "").strip()
    if not current_password:
        frappe.throw(_("Please provide your current password."))

    user = frappe.session.user
    if not user or user == "Guest":
        frappe.throw(_("You must be logged in."))

    try:
        lm = LoginManager()
        lm.authenticate(user=user, pwd=current_password)
    except Exception:
        frappe.clear_messages()
        frappe.throw(_("Current password is incorrect."))

    return {"ok": True}


@frappe.whitelist()
def change_password(current_password: str, new_password: str):
    current_password = (current_password or '').strip()
    new_password = (new_password or '').strip()
    if not current_password or not new_password:
        frappe.throw(_("Both current and new passwords are required."))

    user = frappe.session.user
    if not user or user == "Guest":
        frappe.throw(_("You must be logged in."))

    try:
        lm = LoginManager()
        lm.authenticate(user=user, pwd=current_password)
    except Exception:
        frappe.clear_messages()
        frappe.throw(_("Current password is incorrect."))

    update_password(user, new_password)
    frappe.db.commit()
    return {"ok": True}
