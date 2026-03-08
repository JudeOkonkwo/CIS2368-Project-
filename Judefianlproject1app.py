import flask
import sqlite3
from flask import jsonify
from flask import request

app = flask.Flask(__name__)
app.config["DEBUG"] = True

levels = {
    "Bronze": 1,
    "Silver": 2,
    "Gold": 3
}

def create_connection():
    conn = sqlite3.connect("vip.db")
    conn.row_factory = sqlite3.Row
    return conn

def setup_database():
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS member(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            details TEXT,
            title TEXT,
            level TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS event(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            capacity INTEGER NOT NULL,
            level TEXT NOT NULL,
            date TEXT NOT NULL UNIQUE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS registration(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id INTEGER NOT NULL,
            member_id INTEGER NOT NULL,
            UNIQUE(event_id, member_id)
        )
    """)

    conn.commit()
    conn.close()

setup_database()

@app.route("/", methods=["GET"])
def home():
    return "<h1>VIP Event and Membership Manager API</h1>"

@app.route("/api/member/all", methods=["GET"])
def get_all_members():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM member")
    rows = cursor.fetchall()
    results = []

    for row in rows:
        results.append(dict(row))

    conn.close()
    return jsonify(results)

@app.route("/api/member", methods=["GET"])
def get_member_by_id():
    if "id" in request.args:
        id = int(request.args["id"])
    else:
        return "ERROR"

    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM member WHERE id = ?", (id,))
    rows = cursor.fetchall()
    results = []

    for row in rows:
        results.append(dict(row))

    conn.close()
    return jsonify(results)

@app.route("/api/member", methods=["POST"])
def add_member():
    data = request.get_json()
    name = data["name"]
    details = data["details"]
    title = data["title"]
    level = data["level"]

    if level not in levels:
        return "ERROR"

    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO member (name, details, title, level) VALUES (?, ?, ?, ?)",
        (name, details, title, level)
    )
    conn.commit()
    conn.close()
    return "SUCCESS"

@app.route("/api/member", methods=["PUT"])
def update_member():
    data = request.get_json()
    id = data["id"]
    name = data["name"]
    details = data["details"]
    title = data["title"]
    level = data["level"]

    if level not in levels:
        return "ERROR"

    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE member SET name = ?, details = ?, title = ?, level = ? WHERE id = ?",
        (name, details, title, level, id)
    )
    conn.commit()
    conn.close()
    return "SUCCESS"

@app.route("/api/member", methods=["DELETE"])
def delete_member():
    data = request.get_json()
    id = data["id"]

    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM registration WHERE member_id = ?", (id,))
    cursor.execute("DELETE FROM member WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return "SUCCESS"

@app.route("/api/event/all", methods=["GET"])
def get_all_events():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM event")
    rows = cursor.fetchall()
    results = []

    for row in rows:
        results.append(dict(row))

    conn.close()
    return jsonify(results)

@app.route("/api/event", methods=["GET"])
def get_event_by_id():
    if "id" in request.args:
        id = int(request.args["id"])
    else:
        return "ERROR"

    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM event WHERE id = ?", (id,))
    rows = cursor.fetchall()
    results = []

    for row in rows:
        results.append(dict(row))

    conn.close()
    return jsonify(results)

@app.route("/api/event", methods=["POST"])
def add_event():
    data = request.get_json()
    name = data["name"]
    capacity = data["capacity"]
    level = data["level"]
    date = data["date"]

    if level not in levels:
        return "ERROR"

    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM event WHERE date = ?", (date,))
    rows = cursor.fetchall()

    if len(rows) > 0:
        conn.close()
        return "ERROR: event already exists on this date"

    cursor.execute(
        "INSERT INTO event (name, capacity, level, date) VALUES (?, ?, ?, ?)",
        (name, capacity, level, date)
    )
    conn.commit()
    conn.close()
    return "SUCCESS"

@app.route("/api/event", methods=["PUT"])
def update_event():
    data = request.get_json()
    id = data["id"]
    name = data["name"]
    capacity = data["capacity"]
    level = data["level"]
    date = data["date"]

    if level not in levels:
        return "ERROR"

    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM event WHERE date = ? AND id != ?", (date, id))
    rows = cursor.fetchall()

    if len(rows) > 0:
        conn.close()
        return "ERROR: event already exists on this date"

    cursor.execute(
        "UPDATE event SET name = ?, capacity = ?, level = ?, date = ? WHERE id = ?",
        (name, capacity, level, date, id)
    )
    conn.commit()
    conn.close()
    return "SUCCESS"

@app.route("/api/event", methods=["DELETE"])
def delete_event():
    data = request.get_json()
    id = data["id"]

    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM registration WHERE event_id = ?", (id,))
    cursor.execute("DELETE FROM event WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return "SUCCESS"

@app.route("/api/registration/all", methods=["GET"])
def get_all_registrations():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM registration")
    rows = cursor.fetchall()
    results = []

    for row in rows:
        results.append(dict(row))

    conn.close()
    return jsonify(results)

@app.route("/api/registration", methods=["GET"])
def get_registration_by_id():
    if "id" in request.args:
        id = int(request.args["id"])
    else:
        return "ERROR"

    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM registration WHERE id = ?", (id,))
    rows = cursor.fetchall()
    results = []

    for row in rows:
        results.append(dict(row))

    conn.close()
    return jsonify(results)

@app.route("/api/registration", methods=["POST"])
def add_registration():
    data = request.get_json()
    event_id = data["event_id"]
    member_id = data["member_id"]

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM member WHERE id = ?", (member_id,))
    member_rows = cursor.fetchall()
    if len(member_rows) == 0:
        conn.close()
        return "ERROR: member not found"

    cursor.execute("SELECT * FROM event WHERE id = ?", (event_id,))
    event_rows = cursor.fetchall()
    if len(event_rows) == 0:
        conn.close()
        return "ERROR: event not found"

    cursor.execute("SELECT * FROM registration WHERE event_id = ? AND member_id = ?", (event_id, member_id))
    duplicate_rows = cursor.fetchall()
    if len(duplicate_rows) > 0:
        conn.close()
        return "ERROR: member already registered for this event"

    member = dict(member_rows[0])
    event = dict(event_rows[0])

    if levels[member["level"]] < levels[event["level"]]:
        conn.close()
        return "ERROR: member level too low"

    cursor.execute("SELECT COUNT(*) AS total FROM registration WHERE event_id = ?", (event_id,))
    count_row = cursor.fetchone()
    if count_row["total"] >= event["capacity"]:
        conn.close()
        return "ERROR: event is full"

    cursor.execute(
        "INSERT INTO registration (event_id, member_id) VALUES (?, ?)",
        (event_id, member_id)
    )
    conn.commit()
    conn.close()
    return "SUCCESS"

@app.route("/api/registration", methods=["PUT"])
def update_registration():
    data = request.get_json()
    id = data["id"]
    event_id = data["event_id"]
    member_id = data["member_id"]

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM member WHERE id = ?", (member_id,))
    member_rows = cursor.fetchall()
    if len(member_rows) == 0:
        conn.close()
        return "ERROR: member not found"

    cursor.execute("SELECT * FROM event WHERE id = ?", (event_id,))
    event_rows = cursor.fetchall()
    if len(event_rows) == 0:
        conn.close()
        return "ERROR: event not found"

    cursor.execute("SELECT * FROM registration WHERE event_id = ? AND member_id = ? AND id != ?", (event_id, member_id, id))
    duplicate_rows = cursor.fetchall()
    if len(duplicate_rows) > 0:
        conn.close()
        return "ERROR: member already registered for this event"

    member = dict(member_rows[0])
    event = dict(event_rows[0])

    if levels[member["level"]] < levels[event["level"]]:
        conn.close()
        return "ERROR: member level too low"

    cursor.execute("SELECT COUNT(*) AS total FROM registration WHERE event_id = ? AND id != ?", (event_id, id))
    count_row = cursor.fetchone()
    if count_row["total"] >= event["capacity"]:
        conn.close()
        return "ERROR: event is full"

    cursor.execute(
        "UPDATE registration SET event_id = ?, member_id = ? WHERE id = ?",
        (event_id, member_id, id)
    )
    conn.commit()
    conn.close()
    return "SUCCESS"

@app.route("/api/registration", methods=["DELETE"])
def delete_registration():
    data = request.get_json()
    id = data["id"]

    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM registration WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return "SUCCESS"

@app.route("/api/eventmembers", methods=["GET"])
def get_event_members():
    if "id" in request.args:
        id = int(request.args["id"])
    else:
        return "ERROR"

    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT member.*
        FROM registration
        JOIN member ON registration.member_id = member.id
        WHERE registration.event_id = ?
    """, (id,))
    rows = cursor.fetchall()
    results = []

    for row in rows:
        results.append(dict(row))

    conn.close()
    return jsonify(results)

app.run()