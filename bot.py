import os
import re
import sqlite3
import secrets
import time
from functools import wraps
from flask import Flask, request, redirect, url_for, session, render_template_string, flash, abort

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.environ.get("DATABASE_PATH", os.path.join(APP_DIR, "bots.db"))
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "")
SECRET_KEY = os.environ.get("SECRET_KEY", "")
PORT = int(os.environ.get("PORT", "5000"))

app = Flask(__name__)
app.secret_key = SECRET_KEY or secrets.token_hex(32)
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=os.environ.get("COOKIE_SECURE", "0") == "1",
    MAX_CONTENT_LENGTH=1 * 1024 * 1024,
)

DEFAULT_BOTS = [
    ("Friendship", "Friendshipv2bot", "Community", "Meet and connect with people.", ""),
    ("Nexora", "Nexora_v1_bot", "Utility", "Nexora Telegram bot.", ""),
    ("Giveaway", "Giveaway_561_bot", "Giveaway", "Giveaway bot.", ""),
    ("Leena", "Miss_leena_v1_bot", "Management", "Leena Telegram assistant.", ""),
    ("Nexora 2", "Nexora2bot", "Utility", "Nexora bot.", ""),
    ("Sony GF", "Sonygfbot", "Entertainment", "Entertainment bot.", ""),
    ("Camera Hack", "Camerahack_137_bot", "Utility", "Telegram bot.", ""),
    ("Nexora V5", "Nexora_v5_bot", "Utility", "Nexora V5 bot.", ""),
    ("Request Accept", "Request_123_accept_bot", "Utility", "Request management bot.", ""),
    ("Eisannns", "Eisannnsbot", "Entertainment", "Telegram bot.", ""),
]
OWNER_URL = "https://t.me/Legend_boy_3"

def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with db() as con:
        con.execute("""CREATE TABLE IF NOT EXISTS bots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            username TEXT NOT NULL UNIQUE,
            category TEXT NOT NULL DEFAULT 'Other',
            description TEXT NOT NULL DEFAULT '',
            avatar_url TEXT NOT NULL DEFAULT '',
            created_at INTEGER NOT NULL
        )""")
        count = con.execute("SELECT COUNT(*) FROM bots").fetchone()[0]
        if count == 0:
            for name, username, category, description, avatar in DEFAULT_BOTS:
                con.execute(
                    "INSERT INTO bots(name, username, category, description, avatar_url, created_at) VALUES(?,?,?,?,?,?)",
                    (name, username, category, description, avatar, int(time.time()))
                )

def require_admin(fn):
    @wraps(fn)
    def wrapped(*args, **kwargs):
        if not session.get("admin"):
            return redirect(url_for("login", next=request.path))
        return fn(*args, **kwargs)
    return wrapped

def safe_username(value):
    value = value.strip().lstrip("@")
    if not re.fullmatch(r"[A-Za-z0-9_]{5,32}", value):
        raise ValueError("Username must contain 5–32 letters, numbers, or underscores.")
    return value

def safe_url(value):
    value = value.strip()
    if not value:
        return ""
    if not (value.startswith("https://") or value.startswith("http://")):
        raise ValueError("Avatar URL must start with https:// or http://.")
    return value

STYLE = """
:root{color-scheme:dark;--bg:#080b16;--panel:#11172a;--line:#273252;--text:#eef2ff;--muted:#a6b0ce;--cyan:#56e7ff;--purple:#9b7bff}
*{box-sizing:border-box}body{margin:0;background:radial-gradient(ellipse at top,#1b2450 0,#080b16 55%);font-family:Inter,system-ui,-apple-system,Segoe UI,sans-serif;color:var(--text);min-height:100vh}
a{color:inherit;text-decoration:none}.wrap{max-width:1120px;margin:auto;padding:24px}
header{display:flex;align-items:center;justify-content:space-between;gap:18px;padding:12px 0 28px}.brand{font-weight:900;letter-spacing:.08em;font-size:clamp(18px,3vw,27px)}.brand span{color:var(--cyan)}.pill{border:1px solid var(--line);padding:10px 15px;border-radius:999px;color:var(--muted);font-size:13px}
.hero{padding:30px 0 26px}.eyebrow{color:var(--cyan);font-size:12px;letter-spacing:.22em;font-weight:800}.hero h1{font-size:clamp(36px,7vw,66px);line-height:1.02;margin:12px 0;background:linear-gradient(100deg,#fff,#9edfff 55%,#b5a3ff);color:transparent;background-clip:text}.hero p{color:var(--muted);max-width:620px;line-height:1.7}
.tools{display:flex;gap:12px;flex-wrap:wrap;margin:22px 0}.input{background:#0e1426;border:1px solid var(--line);border-radius:13px;padding:13px 15px;color:var(--text);font:inherit;min-width:0;width:100%;outline:none}.input:focus{border-color:var(--cyan)}.search{flex:1;min-width:220px}.select{width:auto;min-width:150px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(245px,1fr));gap:16px}.card{background:linear-gradient(145deg,rgba(23,31,58,.96),rgba(13,18,35,.97));border:1px solid var(--line);border-radius:20px;padding:20px;box-shadow:0 14px 40px #0002;display:flex;flex-direction:column;min-height:230px}.top{display:flex;align-items:center;gap:13px}.avatar{height:52px;width:52px;border-radius:16px;object-fit:cover;background:#20294a;display:grid;place-items:center;font-size:20px;font-weight:900;color:var(--cyan);border:1px solid #344269;flex-shrink:0}.card h2{font-size:18px;margin:0 0 5px}.handle{font-size:12px;color:var(--cyan)}.tag{font-size:11px;color:#c9bbff;background:#302852;border:1px solid #4a3d76;padding:5px 9px;border-radius:99px;display:inline-block;margin-top:15px;align-self:flex-start}.desc{font-size:13px;color:var(--muted);line-height:1.55;flex:1;margin:12px 0 18px}.btn{display:inline-flex;justify-content:center;align-items:center;gap:8px;border:0;border-radius:12px;padding:12px 16px;background:linear-gradient(100deg,#4adff4,#8d78ff);color:#080d1b;font-weight:850;cursor:pointer;font:inherit;font-size:13px}.btn:hover{filter:brightness(1.08)}.btn.secondary{background:#1b2440;color:var(--text);border:1px solid var(--line)}.actions{display:flex;gap:8px;flex-wrap:wrap}.empty{padding:40px;text-align:center;color:var(--muted);border:1px dashed var(--line);border-radius:18px}
footer{margin-top:38px;border-top:1px solid var(--line);padding:22px 0;color:var(--muted);font-size:12px;display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap}
.panel{max-width:620px;margin:30px auto;background:var(--panel);border:1px solid var(--line);padding:24px;border-radius:20px}.panel h1{margin-top:0}.field{margin:14px 0}.field label{display:block;color:var(--muted);font-size:13px;margin-bottom:7px}.flash{background:#332445;border:1px solid #654d83;padding:11px 13px;border-radius:10px;margin:10px 0;font-size:13px}.admin-list{width:100%;border-collapse:collapse;margin-top:18px;font-size:13px}.admin-list th,.admin-list td{text-align:left;padding:10px;border-bottom:1px solid var(--line)}.admin-list th{color:var(--muted)}.small{font-size:12px;color:var(--muted)}@media(max-width:600px){.wrap{padding:16px}.pill{font-size:11px;padding:8px 10px}.admin-list{display:block;overflow-x:auto}}
"""
BASE = """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#080b16"><title>{{ title }} · RAJIV TG BOTS</title><style>""" + STYLE + """</style></head><body><div class="wrap">{% with messages = get_flashed_messages() %}{% for message in messages %}<div class="flash">{{ message }}</div>{% endfor %}{% endwith %}{{ body|safe }}</div></body></html>"""

HOME_BODY = """
<header><a class="brand" href="{{ url_for('home') }}">RAJIV <span>TG BOTS</span></a><a class="pill" href="{{ owner_url }}" target="_blank" rel="noopener">OWNER ↗</a></header>
<section class="hero"><div class="eyebrow">TELEGRAM BOT DIRECTORY</div><h1>Your bots.<br>One place.</h1><p>Explore the Rajiv Telegram bot collection. Find a bot, check what it does, and open it directly in Telegram.</p></section>
<div class="tools"><input class="input search" id="search" placeholder="Search bots by name or username…" autocomplete="off"><select class="input select" id="category"><option value="">All categories</option>{% for c in categories %}<option>{{ c }}</option>{% endfor %}</select></div>
<div class="grid" id="grid">{% for b in bots %}<article class="card" data-name="{{ (b.name ~ ' ' ~ b.username ~ ' ' ~ b.category ~ ' ' ~ b.description)|lower }}"><div class="top">{% if b.avatar_url %}<img class="avatar" src="{{ b.avatar_url|e }}" alt="" loading="lazy" onerror="this.style.display='none';this.nextElementSibling.style.display='grid'"><div class="avatar" style="display:none">{{ b.name[:1]|upper }}</div>{% else %}<div class="avatar">{{ b.name[:1]|upper }}</div>{% endif %}<div><h2>{{ b.name }}</h2><div class="handle">@{{ b.username }}</div></div></div><span class="tag">{{ b.category }}</span><p class="desc">{{ b.description or 'Open this bot on Telegram.' }}</p><a class="btn" href="https://t.me/{{ b.username }}" target="_blank" rel="noopener">OPEN BOT ↗</a></article>{% endfor %}</div><div class="empty" id="empty" hidden>No bots match your search.</div>
<footer><span>© {{ year }} RAJIV TG BOTS</span><span>Built for Telegram · <a href="{{ url_for('login') }}">Admin</a></span></footer>
<script>
const search=document.getElementById('search'),category=document.getElementById('category'),cards=[...document.querySelectorAll('.card')],empty=document.getElementById('empty');
function filter(){let q=search.value.toLowerCase().trim(),c=category.value.toLowerCase(),n=0;cards.forEach(card=>{let show=card.dataset.name.includes(q)&&(!c||card.querySelector('.tag').textContent.toLowerCase()===c);card.hidden=!show;if(show)n++});empty.hidden=n!==0}
search.addEventListener('input',filter);category.addEventListener('change',filter);
</script>
"""

LOGIN_BODY = """
<header><a class="brand" href="{{ url_for('home') }}">RAJIV <span>TG BOTS</span></a><a class="pill" href="{{ url_for('home') }}">← Website</a></header>
<div class="panel"><div class="eyebrow">PRIVATE AREA</div><h1>Admin login</h1><p class="small">Sign in to manage the bot directory. Set ADMIN_PASSWORD in your hosting environment before deploying.</p><form method="post"><input type="hidden" name="csrf" value="{{ csrf }}"><div class="field"><label>Admin password</label><input class="input" type="password" name="password" required autocomplete="current-password"></div><button class="btn" type="submit">SIGN IN →</button></form></div>
"""

ADMIN_BODY = """
<header><a class="brand" href="{{ url_for('home') }}">RAJIV <span>TG BOTS</span></a><div class="actions"><a class="pill" href="{{ url_for('home') }}">View site</a><form method="post" action="{{ url_for('logout') }}"><input type="hidden" name="csrf" value="{{ csrf }}"><button class="btn secondary" type="submit">Log out</button></form></div></header>
<section class="hero"><div class="eyebrow">DIRECTORY CONTROL</div><h1>Manage bots.</h1><p>Add, edit, or remove listings. Bot avatar images can be set using a public HTTPS image URL.</p></section>
<div class="panel" style="max-width:none;margin:0"><h2>{{ 'Edit bot' if edit_bot else 'Add a bot' }}</h2><form method="post" action="{{ url_for('save_bot', bot_id=edit_bot.id) if edit_bot else url_for('save_bot') }}"><input type="hidden" name="csrf" value="{{ csrf }}">
<div class="field"><label>Display name</label><input class="input" name="name" maxlength="80" required value="{{ edit_bot.name if edit_bot else '' }}"></div>
<div class="field"><label>Telegram username (without @)</label><input class="input" name="username" maxlength="32" required value="{{ edit_bot.username if edit_bot else '' }}" placeholder="ExampleBot"></div>
<div class="field"><label>Category</label><input class="input" name="category" maxlength="40" required value="{{ edit_bot.category if edit_bot else 'Other' }}"></div>
<div class="field"><label>Description</label><textarea class="input" name="description" rows="3" maxlength="300">{{ edit_bot.description if edit_bot else '' }}</textarea></div>
<div class="field"><label>Avatar image URL (optional)</label><input class="input" type="url" name="avatar_url" value="{{ edit_bot.avatar_url if edit_bot else '' }}" placeholder="https://…"></div>
<button class="btn" type="submit">{{ 'Save changes' if edit_bot else 'Add bot' }}</button>{% if edit_bot %} <a class="btn secondary" href="{{ url_for('admin') }}">Cancel</a>{% endif %}</form></div>
<h2 style="margin-top:30px">Current bots ({{ bots|length }})</h2><table class="admin-list"><thead><tr><th>Bot</th><th>Category</th><th>Actions</th></tr></thead><tbody>{% for b in bots %}<tr><td><strong>{{ b.name }}</strong><br><span class="small">@{{ b.username }}</span></td><td>{{ b.category }}</td><td><div class="actions"><a class="btn secondary" href="{{ url_for('admin', edit=b.id) }}">Edit</a><form method="post" action="{{ url_for('delete_bot', bot_id=b.id) }}" onsubmit="return confirm('Delete this bot listing?')"><input type="hidden" name="csrf" value="{{ csrf }}"><button class="btn secondary" type="submit">Delete</button></form></div></td></tr>{% endfor %}</tbody></table><footer><span>Admin panel · RAJIV TG BOTS</span><span>Keep credentials private</span></footer>
"""

def render_page(title, body_template, **context):
    context.setdefault("owner_url", OWNER_URL)
    context.setdefault("year", time.gmtime().tm_year)
    context.setdefault("csrf", session.setdefault("csrf", secrets.token_urlsafe(24)))
    body = render_template_string(body_template, **context)
    return render_template_string(BASE, title=title, body=body)

def check_csrf():
    sent = request.form.get("csrf", "")
    saved = session.get("csrf", "")
    if not sent or not saved or not secrets.compare_digest(sent, saved):
        abort(400, "Invalid form token. Refresh the page and try again.")

@app.after_request
def security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    return response

@app.route("/")
def home():
    with db() as con:
        bots = con.execute("SELECT * FROM bots ORDER BY name COLLATE NOCASE").fetchall()
    categories = sorted({b["category"] for b in bots}, key=str.lower)
    return render_page("Bot directory", HOME_BODY, bots=bots, categories=categories)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        check_csrf()
        if not ADMIN_PASSWORD:
            flash("Admin login is disabled until ADMIN_PASSWORD is set in the environment.")
            return redirect(url_for("login"))
        if secrets.compare_digest(request.form.get("password", ""), ADMIN_PASSWORD):
            session.clear()
            session["admin"] = True
            session["csrf"] = secrets.token_urlsafe(24)
            return redirect(url_for("admin"))
        time.sleep(0.6)
        flash("Incorrect password.")
    return render_page("Admin login", LOGIN_BODY)

@app.route("/admin")
@require_admin
def admin():
    with db() as con:
        bots = con.execute("SELECT * FROM bots ORDER BY name COLLATE NOCASE").fetchall()
        edit_id = request.args.get("edit", type=int)
        edit_bot = con.execute("SELECT * FROM bots WHERE id=?", (edit_id,)).fetchone() if edit_id else None
    return render_page("Admin panel", ADMIN_BODY, bots=bots, edit_bot=edit_bot)

@app.route("/admin/save", methods=["POST"])
@app.route("/admin/save/<int:bot_id>", methods=["POST"])
@require_admin
def save_bot(bot_id=None):
    check_csrf()
    try:
        name = request.form.get("name", "").strip()
        username = safe_username(request.form.get("username", ""))
        category = request.form.get("category", "").strip() or "Other"
        description = request.form.get("description", "").strip()
        avatar_url = safe_url(request.form.get("avatar_url", ""))
        if not name or len(name) > 80 or len(category) > 40 or len(description) > 300:
            raise ValueError("Name, category, or description is missing or too long.")
        with db() as con:
            if bot_id:
                cur = con.execute("UPDATE bots SET name=?,username=?,category=?,description=?,avatar_url=? WHERE id=?",
                                  (name, username, category, description, avatar_url, bot_id))
                if cur.rowcount == 0:
                    abort(404)
            else:
                con.execute("INSERT INTO bots(name,username,category,description,avatar_url,created_at) VALUES(?,?,?,?,?,?)",
                            (name, username, category, description, avatar_url, int(time.time())))
        flash("Bot listing saved.")
    except sqlite3.IntegrityError:
        flash("That Telegram username is already listed.")
    except ValueError as exc:
        flash(str(exc))
    return redirect(url_for("admin"))

@app.route("/admin/delete/<int:bot_id>", methods=["POST"])
@require_admin
def delete_bot(bot_id):
    check_csrf()
    with db() as con:
        con.execute("DELETE FROM bots WHERE id=?", (bot_id,))
    flash("Bot listing deleted.")
    return redirect(url_for("admin"))

@app.route("/logout", methods=["POST"])
@require_admin
def logout():
    check_csrf()
    session.clear()
    return redirect(url_for("home"))

@app.get("/health")
def health():
    return {"status": "ok"}

init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT, debug=False)
