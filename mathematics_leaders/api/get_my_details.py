
import frappe

@frappe.whitelist(allow_guest=True)
def get_me():
    """يرجع بيانات جلسة المستخدم الحالي (من DocType User).
    إذا كان المستخدم Guest نرجع ok=False ليعيدك لصفحة الدخول من الواجهة.
    """
    user = frappe.session.user or "Guest"
    if not user or user == "Guest":
        return {"ok": False, "profile": None}

    # الحقول التي نريدها من User
    row = frappe.db.get_value(
        "User",
        user,
        ["name", "username", "full_name", "first_name", "language", "email"],
        as_dict=True,
    ) or {}

    # fallback للاسم
    display = row.get("full_name") or row.get("first_name") or row.get("username") or row.get("name")

    return {
        "ok": True,
        "profile": {
            "user": row.get("name"),
            "username": row.get("username") or row.get("email") or row.get("name"),
            "full_name": display,
            "language": row.get("language") or "ar",
        },
    }
