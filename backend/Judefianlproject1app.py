from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)

DB_NAME = "vip.db"

levels = {
    "Bronze": 1,
    "Silver": 2,
    "Gold": 3
}


def create_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def setup_database():
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS member (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            details TEXT,
            title TEXT,
            level TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS event (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            capacity INTEGER NOT NULL,
            level TEXT NOT NULL,
            date TEXT NOT NULL UNIQUE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS registration (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id INTEGER NOT NULL,
            member_id INTEGER NOT NULL,
            UNIQUE(event_id, member_id),
            FOREIGN KEY(event_id) REFERENCES event(id),
            FOREIGN KEY(member_id) REFERENCES member(id)
        )
    """)

    conn.commit()
    conn.close()


def row_list(rows):
    return [dict(row) for row in rows]


def valid_level(level):
    return level in levels


setup_database()


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "VIP Event and Membership Manager API is running"
    })


# -------------------------
# MEMBER ROUTES
# -------------------------

@app.route("/api/member/all", methods=["GET"])
def get_all_members():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM member ORDER BY name")
    rows = cursor.fetchall()
    conn.close()
    return jsonify(row_list(rows))


@app.route("/api/member", methods=["GET"])
def get_member_by_id():
    member_id = request.args.get("id")

    if not member_id:
        return jsonify({"error": "Member id is required"}), 400

    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM member WHERE id = ?", (member_id,))
    row = cursor.fetchone()
    conn.close()

    if row is None:
        return jsonify({"error": "Member not found"}), 404

    return jsonify(dict(row))


@app.route("/api/member", methods=["POST"])
def add_member():
    data = request.get_json()

    name = data.get("name")
    details = data.get("details", "")
    title = data.get("title", "")
    level = data.get("level")

    if not name or not level:
        return jsonify({"error": "Name and level are required"}), 400

    if not valid_level(level):
        return jsonify({"error": "Invalid membership level"}), 400

    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO member (name, details, title, level) VALUES (?, ?, ?, ?)",
        (name, details, title, level)
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()

    return jsonify({
        "message": "Member created successfully",
        "id": new_id
    }), 201


@app.route("/api/member", methods=["PUT"])
def update_member():
    data = request.get_json()

    member_id = data.get("id")
    name = data.get("name")
    details = data.get("details", "")
    title = data.get("title", "")
    level = data.get("level")

    if not member_id or not name or not level:
        return jsonify({"error": "Member id, name, and level are required"}), 400

    if not valid_level(level):
        return jsonify({"error": "Invalid membership level"}), 400

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM member WHERE id = ?", (member_id,))
    existing_member = cursor.fetchone()

    if existing_member is None:
        conn.close()
        return jsonify({"error": "Member not found"}), 404

    cursor.execute(
        "UPDATE member SET name = ?, details = ?, title = ?, level = ? WHERE id = ?",
        (name, details, title, level, member_id)
    )

    conn.commit()
    conn.close()

    return jsonify({"message": "Member updated successfully"})


@app.route("/api/member", methods=["DELETE"])
def delete_member():
    data = request.get_json()
    member_id = data.get("id")

    if not member_id:
        return jsonify({"error": "Member id is required"}), 400

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM member WHERE id = ?", (member_id,))
    existing_member = cursor.fetchone()

    if existing_member is None:
        conn.close()
        return jsonify({"error": "Member not found"}), 404

    cursor.execute("DELETE FROM registration WHERE member_id = ?", (member_id,))
    cursor.execute("DELETE FROM member WHERE id = ?", (member_id,))

    conn.commit()
    conn.close()

    return jsonify({"message": "Member deleted successfully"})


# -------------------------
# EVENT ROUTES
# -------------------------

@app.route("/api/event/all", methods=["GET"])
def get_all_events():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM event ORDER BY date")
    rows = cursor.fetchall()
    conn.close()
    return jsonify(row_list(rows))


@app.route("/api/event", methods=["GET"])
def get_event_by_id():
    event_id = request.args.get("id")

    if not event_id:
        return jsonify({"error": "Event id is required"}), 400

    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM event WHERE id = ?", (event_id,))
    row = cursor.fetchone()
    conn.close()

    if row is None:
        return jsonify({"error": "Event not found"}), 404

    return jsonify(dict(row))


@app.route("/api/event", methods=["POST"])
def add_event():
    data = request.get_json()

    name = data.get("name")
    capacity = data.get("capacity")
    level = data.get("level")
    date = data.get("date")

    if not name or not capacity or not level or not date:
        return jsonify({"error": "Name, capacity, level, and date are required"}), 400

    if not valid_level(level):
        return jsonify({"error": "Invalid event level"}), 400

    if int(capacity) <= 0:
        return jsonify({"error": "Capacity must be greater than zero"}), 400

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM event WHERE date = ?", (date,))
    duplicate_event = cursor.fetchone()

    if duplicate_event is not None:
        conn.close()
        return jsonify({"error": "An event already exists on this date"}), 400

    cursor.execute(
        "INSERT INTO event (name, capacity, level, date) VALUES (?, ?, ?, ?)",
        (name, capacity, level, date)
    )

    conn.commit()
    new_id = cursor.lastrowid
    conn.close()

    return jsonify({
        "message": "Event created successfully",
        "id": new_id
    }), 201


@app.route("/api/event", methods=["PUT"])
def update_event():
    data = request.get_json()

    event_id = data.get("id")
    name = data.get("name")
    capacity = data.get("capacity")
    level = data.get("level")
    date = data.get("date")

    if not event_id or not name or not capacity or not level or not date:
        return jsonify({"error": "Event id, name, capacity, level, and date are required"}), 400

    if not valid_level(level):
        return jsonify({"error": "Invalid event level"}), 400

    if int(capacity) <= 0:
        return jsonify({"error": "Capacity must be greater than zero"}), 400

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM event WHERE id = ?", (event_id,))
    existing_event = cursor.fetchone()

    if existing_event is None:
        conn.close()
        return jsonify({"error": "Event not found"}), 404

    cursor.execute("SELECT * FROM event WHERE date = ? AND id != ?", (date, event_id))
    duplicate_event = cursor.fetchone()

    if duplicate_event is not None:
        conn.close()
        return jsonify({"error": "An event already exists on this date"}), 400

    cursor.execute(
        "UPDATE event SET name = ?, capacity = ?, level = ?, date = ? WHERE id = ?",
        (name, capacity, level, date, event_id)
    )

    conn.commit()
    conn.close()

    return jsonify({"message": "Event updated successfully"})


@app.route("/api/event", methods=["DELETE"])
def delete_event():
    data = request.get_json()
    event_id = data.get("id")

    if not event_id:
        return jsonify({"error": "Event id is required"}), 400

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM event WHERE id = ?", (event_id,))
    existing_event = cursor.fetchone()

    if existing_event is None:
        conn.close()
        return jsonify({"error": "Event not found"}), 404

    cursor.execute("DELETE FROM registration WHERE event_id = ?", (event_id,))
    cursor.execute("DELETE FROM event WHERE id = ?", (event_id,))

    conn.commit()
    conn.close()

    return jsonify({"message": "Event deleted successfully"})


# -------------------------
# REGISTRATION ROUTES
# -------------------------

@app.route("/api/registration/all", methods=["GET"])
def get_all_registrations():
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            registration.id,
            registration.event_id,
            registration.member_id,
            event.name AS event_name,
            event.date AS event_date,
            member.name AS member_name,
            member.level AS member_level
        FROM registration
        JOIN event ON registration.event_id = event.id
        JOIN member ON registration.member_id = member.id
        ORDER BY event.date, member.name
    """)

    rows = cursor.fetchall()
    conn.close()

    return jsonify(row_list(rows))


@app.route("/api/registration", methods=["GET"])
def get_registration_by_id():
    registration_id = request.args.get("id")

    if not registration_id:
        return jsonify({"error": "Registration id is required"}), 400

    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM registration WHERE id = ?", (registration_id,))
    row = cursor.fetchone()
    conn.close()

    if row is None:
        return jsonify({"error": "Registration not found"}), 404

    return jsonify(dict(row))


@app.route("/api/registration", methods=["POST"])
def add_registration():
    data = request.get_json()

    event_id = data.get("event_id")
    member_id = data.get("member_id")

    if not event_id or not member_id:
        return jsonify({"error": "Event and member are required"}), 400

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM member WHERE id = ?", (member_id,))
    member = cursor.fetchone()

    if member is None:
        conn.close()
        return jsonify({"error": "Member not found"}), 404

    cursor.execute("SELECT * FROM event WHERE id = ?", (event_id,))
    event = cursor.fetchone()

    if event is None:
        conn.close()
        return jsonify({"error": "Event not found"}), 404

    cursor.execute(
        "SELECT * FROM registration WHERE event_id = ? AND member_id = ?",
        (event_id, member_id)
    )
    duplicate_registration = cursor.fetchone()

    if duplicate_registration is not None:
        conn.close()
        return jsonify({"error": "Member is already registered for this event"}), 400

    if levels[member["level"]] < levels[event["level"]]:
        conn.close()
        return jsonify({"error": "Member level is too low for this event"}), 400

    cursor.execute(
        "SELECT COUNT(*) AS total FROM registration WHERE event_id = ?",
        (event_id,)
    )
    count_row = cursor.fetchone()

    if count_row["total"] >= event["capacity"]:
        conn.close()
        return jsonify({"error": "Event is already at full capacity"}), 400

    cursor.execute(
        "INSERT INTO registration (event_id, member_id) VALUES (?, ?)",
        (event_id, member_id)
    )

    conn.commit()
    new_id = cursor.lastrowid
    conn.close()

    return jsonify({
        "message": "Registration created successfully",
        "id": new_id
    }), 201


@app.route("/api/registration", methods=["PUT"])
def update_registration():
    data = request.get_json()

    registration_id = data.get("id")
    event_id = data.get("event_id")
    member_id = data.get("member_id")

    if not registration_id or not event_id or not member_id:
        return jsonify({"error": "Registration id, event, and member are required"}), 400

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM registration WHERE id = ?", (registration_id,))
    existing_registration = cursor.fetchone()

    if existing_registration is None:
        conn.close()
        return jsonify({"error": "Registration not found"}), 404

    cursor.execute("SELECT * FROM member WHERE id = ?", (member_id,))
    member = cursor.fetchone()

    if member is None:
        conn.close()
        return jsonify({"error": "Member not found"}), 404

    cursor.execute("SELECT * FROM event WHERE id = ?", (event_id,))
    event = cursor.fetchone()

    if event is None:
        conn.close()
        return jsonify({"error": "Event not found"}), 404

    cursor.execute(
        "SELECT * FROM registration WHERE event_id = ? AND member_id = ? AND id != ?",
        (event_id, member_id, registration_id)
    )
    duplicate_registration = cursor.fetchone()

    if duplicate_registration is not None:
        conn.close()
        return jsonify({"error": "Member is already registered for this event"}), 400

    if levels[member["level"]] < levels[event["level"]]:
        conn.close()
        return jsonify({"error": "Member level is too low for this event"}), 400

    cursor.execute(
        "SELECT COUNT(*) AS total FROM registration WHERE event_id = ? AND id != ?",
        (event_id, registration_id)
    )
    count_row = cursor.fetchone()

    if count_row["total"] >= event["capacity"]:
        conn.close()
        return jsonify({"error": "Event is already at full capacity"}), 400

    cursor.execute(
        "UPDATE registration SET event_id = ?, member_id = ? WHERE id = ?",
        (event_id, member_id, registration_id)
    )

    conn.commit()
    conn.close()

    return jsonify({"message": "Registration updated successfully"})


@app.route("/api/registration", methods=["DELETE"])
def delete_registration():
    data = request.get_json()
    registration_id = data.get("id")

    if not registration_id:
        return jsonify({"error": "Registration id is required"}), 400

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM registration WHERE id = ?", (registration_id,))
    existing_registration = cursor.fetchone()

    if existing_registration is None:
        conn.close()
        return jsonify({"error": "Registration not found"}), 404

    cursor.execute("DELETE FROM registration WHERE id = ?", (registration_id,))

    conn.commit()
    conn.close()

    return jsonify({"message": "Registration deleted successfully"})


# -------------------------
# EVENT MEMBERS ROUTE
# -------------------------

@app.route("/api/eventmembers", methods=["GET"])
def get_event_members():
    event_id = request.args.get("id")

    if not event_id:
        return jsonify({"error": "Event id is required"}), 400

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            member.name,
            member.details,
            member.title,
            member.level
        FROM registration
        JOIN member ON registration.member_id = member.id
        WHERE registration.event_id = ?
        ORDER BY member.name
    """, (event_id,))

    rows = cursor.fetchall()
    conn.close()

    return jsonify(row_list(rows))


if __name__ == "__main__":
    app.run(debug=True, port=5000)
    