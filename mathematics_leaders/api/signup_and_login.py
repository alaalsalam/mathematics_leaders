# apps/mathematics_leaders/mathematics_leaders/api.py
import frappe
from frappe import _
from frappe.utils.password import update_password
from frappe.auth import LoginManager

# ---------- Helpers ----------
def _synthetic_email(username: str) -> str:
    slug = frappe.scrub(username or "player")
    return f"{slug}@ml.local"

def _get_user_by_username(username: str):
    """أعد Doc( User ) إن وجد بالـ username أو بالبريد التركيبي."""
    if not username:
        return None
    name = frappe.db.get_value("User", {"username": username}, "name")
    if name:
        return frappe.get_doc("User", name)
    email = _synthetic_email(username)
    name = frappe.db.get_value("User", {"email": email}, "name")
    return frappe.get_doc("User", name) if name else None

# ---------- Signup ----------
@frappe.whitelist(allow_guest=True)
def signup_user(username: str, password: str, language: str = "ar"):
    """
    إنشاء Website User + سجل في Game Users (بدون تخزين كلمة مرور هناك).
    """
    username = (username or "").strip()
    password = (password or "").strip()
    language = (language or "ar").strip() or "ar"

    if not username or not password:
        frappe.throw(_("Username and password are required."))

    email = _synthetic_email(username)

    if (frappe.db.exists("User", {"email": email})
        or frappe.db.exists("User", {"username": username})):
        frappe.throw(_("User already exists."))

    # 1) User
    user = frappe.get_doc({
        "doctype": "User",
        "email": email,
        "username": username,
        "first_name": username,
        "full_name": username,
        "language": language,
        "user_type": "Website User",
        "enabled": 1,
        "send_welcome_email": 0,
    })
    user.insert(ignore_permissions=True)
    # user.add_roles("Website User")
    update_password(user.name, password)

    # 2) Game Users (تجنّب التكرار)
    if not frappe.db.exists("Game Users", {"username": username}):
        gu = frappe.get_doc({
            "doctype": "Game Users",
            "username": username,
            "language": language,
            "password": password,
            "challenge_points": 0.0,
        })
        gu.insert(ignore_permissions=True)
        game_user_name = gu.name
    else:
        game_user_name = frappe.db.get_value("Game Users", {"username": username}, "name")

    frappe.db.commit()
    return {"ok": True, "user": user.name, "game_user": game_user_name}

# ---------- Login (جلسة حقيقية sid) ----------
@frappe.whitelist(allow_guest=True)
def verify_login(usr: str, pwd: str):
    """
    دخول بكلمة مرور المستخدم (ينشئ sid حقيقية):
    نحاول قبول username أو email.
    """
    usr = (usr or "").strip()
    pwd = (pwd or "").strip()
    if not usr or not pwd:
        frappe.throw(_("Username and password are required."))

    # حوّل username -> user.name إن لزم
    user_doc = _get_user_by_username(usr)
    login_id = user_doc.name if user_doc else usr

    try:
        lm = LoginManager()
        lm.authenticate(user=login_id, pwd=pwd)
        lm.post_login()  # يضبط الجلسة والكوكي sid
    except Exception:
        frappe.clear_messages()
        frappe.throw(_("Invalid credentials"))

    # بيانات بسيطة للاستخدام الأمامي
    username = frappe.db.get_value("User", {"name": frappe.session.user}, "username") or usr
    gu = frappe.db.get_value("Game Users",
                             {"username": username},
                             ["name", "language", "challenge_points"],
                             as_dict=True)
    return {"ok": True, "user": frappe.session.user, "profile": gu}

# ---------- Utilities (اختياري) ----------
@frappe.whitelist(allow_guest=True)
def whoami():
    return {"user": frappe.session.user}

@frappe.whitelist(allow_guest=True)
def logout():
    frappe.local.login_manager.logout()
    frappe.db.commit()
    return {"ok": True}
