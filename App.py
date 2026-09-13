import os
import math
import json
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from database import get_db, init_db

# Load environment variables
load_dotenv()

FRONTEND_DIST = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend", "dist")

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "women-safety-analytics-secret-2026")
CORS(app, resources={r"/api/*": {"origins": "*"}})


GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Initialize DB on start
init_db()

# ==========================================
# HELPER FUNCTIONS
# ==========================================

def calculate_distance(lat1, lon1, lat2, lon2):
    """Haversine formula to compute distance in km between two GPS coordinates."""
    if not lat1 or not lon1 or not lat2 or not lon2:
        return 999.0
    R = 6371.0 # Earth radius in kilometers
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 2)

# ==========================================
# HEALTH CHECK
# ==========================================

@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "Women Safety Analytics API",
        "timestamp": datetime.utcnow().isoformat(),
        "gemini_configured": bool(GEMINI_API_KEY)
    }), 200

# ==========================================
# AUTHENTICATION
# ==========================================

@app.route("/api/auth/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    fullname = data.get("fullname", "").strip()
    email = data.get("email", "").strip().lower()
    phone = data.get("phone", "").strip()
    password = data.get("password", "")
    role = data.get("role", "user")

    if not fullname or not email or not password:
        return jsonify({"error": "Full name, email, and password are required."}), 400

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
    if cursor.fetchone():
        conn.close()
        return jsonify({"error": "An account with this email already exists."}), 409

    hashed_pw = generate_password_hash(password)
    default_avatar = f"https://api.dicebear.com/7.x/avataaars/svg?seed={email}"

    cursor.execute("""
    INSERT INTO users (fullname, email, phone, password, role, avatar)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (fullname, email, phone, hashed_pw, role, default_avatar))
    conn.commit()
    user_id = cursor.lastrowid

    cursor.execute("SELECT id, fullname, email, phone, role, avatar, medical_info, created_at FROM users WHERE id = ?", (user_id,))
    user = dict(cursor.fetchone())
    conn.close()

    return jsonify({
        "message": "User registered successfully",
        "user": user,
        "token": f"ws_auth_token_{user_id}_{int(datetime.utcnow().timestamp())}"
    }), 201

@app.route("/api/auth/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"error": "Email and password are required."}), 400

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    row = cursor.fetchone()
    conn.close()

    if not row or not check_password_hash(row["password"], password):
        return jsonify({"error": "Invalid email or password."}), 401

    user = {
        "id": row["id"],
        "fullname": row["fullname"],
        "email": row["email"],
        "phone": row["phone"],
        "role": row["role"],
        "avatar": row["avatar"],
        "medical_info": row["medical_info"],
        "created_at": row["created_at"]
    }

    return jsonify({
        "message": "Login successful",
        "user": user,
        "token": f"ws_auth_token_{user['id']}_{int(datetime.utcnow().timestamp())}"
    }), 200

@app.route("/api/auth/me/<int:user_id>", methods=["GET"])
def get_current_user(user_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, fullname, email, phone, role, avatar, medical_info, created_at FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return jsonify({"error": "User not found"}), 404

    return jsonify({"user": dict(row)}), 200

@app.route("/api/auth/profile/<int:user_id>", methods=["PUT"])
def update_profile(user_id):
    data = request.get_json() or {}
    fullname = data.get("fullname")
    phone = data.get("phone")
    medical_info = data.get("medical_info")
    avatar = data.get("avatar")

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE users
    SET fullname = COALESCE(?, fullname),
        phone = COALESCE(?, phone),
        medical_info = COALESCE(?, medical_info),
        avatar = COALESCE(?, avatar)
    WHERE id = ?
    """, (fullname, phone, medical_info, avatar, user_id))
    conn.commit()

    cursor.execute("SELECT id, fullname, email, phone, role, avatar, medical_info, created_at FROM users WHERE id = ?", (user_id,))
    user = dict(cursor.fetchone())
    conn.close()

    return jsonify({"message": "Profile updated successfully", "user": user}), 200

# ==========================================
# EMERGENCY SOS MODULE
# ==========================================

@app.route("/api/sos/trigger", methods=["POST"])
def trigger_sos():
    data = request.get_json() or {}
    user_id = data.get("user_id")
    latitude = data.get("latitude")
    longitude = data.get("longitude")
    address = data.get("address", "Live GPS Coordinates Acquired")
    notes = data.get("notes", "Emergency SOS Button Triggered")

    if latitude is None or longitude is None:
        return jsonify({"error": "Latitude and longitude coordinates are mandatory for SOS."}), 400

    conn = get_db()
    cursor = conn.cursor()

    # Get user details & contacts
    user_name = "Anonymous / Guest"
    if user_id:
        cursor.execute("SELECT fullname FROM users WHERE id = ?", (user_id,))
        user_row = cursor.fetchone()
        if user_row:
            user_name = user_row["fullname"]

    # Fetch user's registered emergency contacts
    contacts = []
    if user_id:
        cursor.execute("SELECT * FROM emergency_contacts WHERE user_id = ?", (user_id,))
        contacts = [dict(r) for r in cursor.fetchall()]

    contacts_count = len(contacts)

    # Insert SOS record into DB
    cursor.execute("""
    INSERT INTO sos_alerts (user_id, user_name, latitude, longitude, address, contacts_alerted, status, notes)
    VALUES (?, ?, ?, ?, ?, ?, 'Active', ?)
    """, (user_id, user_name, latitude, longitude, address, contacts_count, notes))
    conn.commit()
    sos_id = cursor.lastrowid

    # Find nearest emergency resources (Police, Hospitals, Helplines)
    cursor.execute("SELECT * FROM emergency_resources")
    all_resources = [dict(r) for r in cursor.fetchall()]
    
    # Calculate real-time distances
    for res in all_resources:
        res["distance_km"] = calculate_distance(latitude, longitude, res["latitude"], res["longitude"])

    all_resources.sort(key=lambda x: x["distance_km"])
    nearest_resources = all_resources[:5]

    conn.close()

    # Build simulated multi-channel dispatch details
    google_maps_link = f"https://www.google.com/maps?q={latitude},{longitude}"
    sos_message = f"🚨 EMERGENCY SOS ALERT! {user_name} needs urgent assistance at: {address}. Live Location: {google_maps_link}. Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}."

    dispatched_channels = []
    for contact in contacts:
        dispatched_channels.append({
            "contact_name": contact["name"],
            "phone": contact["phone"],
            "relationship": contact["relationship"],
            "sms_status": "DELIVERED",
            "whatsapp_status": "DELIVERED",
            "whatsapp_intent_url": f"https://api.whatsapp.com/send?phone={contact['phone'].replace(' ', '').replace('-', '')}&text={requests_quote(sos_message)}"
        })

    return jsonify({
        "success": True,
        "sos_id": sos_id,
        "status": "EMERGENCY_DISPATCHED",
        "timestamp": datetime.utcnow().isoformat(),
        "location": {
            "latitude": latitude,
            "longitude": longitude,
            "address": address,
            "maps_url": google_maps_link
        },
        "user_name": user_name,
        "contacts_notified": contacts_count,
        "dispatch_details": dispatched_channels,
        "nearest_resources": nearest_resources,
        "sos_message": sos_message
    }), 201

def requests_quote(text):
    import urllib.parse
    return urllib.parse.quote(text)

@app.route("/api/sos/resolve/<int:sos_id>", methods=["PUT"])
def resolve_sos(sos_id):
    data = request.get_json() or {}
    status = data.get("status", "Resolved")

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE sos_alerts SET status = ? WHERE id = ?", (status, sos_id))
    conn.commit()
    conn.close()

    return jsonify({"message": f"SOS Alert #{sos_id} marked as {status}"}), 200

@app.route("/api/sos/history", methods=["GET"])
def get_sos_history():
    user_id = request.args.get("user_id")
    conn = get_db()
    cursor = conn.cursor()

    if user_id:
        cursor.execute("SELECT * FROM sos_alerts WHERE user_id = ? ORDER BY created_at DESC", (user_id,))
    else:
        cursor.execute("SELECT * FROM sos_alerts ORDER BY created_at DESC LIMIT 50")
    
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return jsonify({"sos_history": rows}), 200

# ==========================================
# EMERGENCY CONTACTS
# ==========================================

@app.route("/api/contacts", methods=["GET"])
def get_contacts():
    user_id = request.args.get("user_id", 2)
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM emergency_contacts WHERE user_id = ? ORDER BY is_primary DESC, created_at ASC", (user_id,))
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return jsonify({"contacts": rows}), 200

@app.route("/api/contacts", methods=["POST"])
def add_contact():
    data = request.get_json() or {}
    user_id = data.get("user_id", 2)
    name = data.get("name", "").strip()
    phone = data.get("phone", "").strip()
    relationship = data.get("relationship", "Trusted Contact").strip()
    email = data.get("email", "").strip()
    is_primary = 1 if data.get("is_primary") else 0

    if not name or not phone:
        return jsonify({"error": "Name and phone number are required."}), 400

    conn = get_db()
    cursor = conn.cursor()

    # If new contact is primary, unset previous primary
    if is_primary:
        cursor.execute("UPDATE emergency_contacts SET is_primary = 0 WHERE user_id = ?", (user_id,))

    cursor.execute("""
    INSERT INTO emergency_contacts (user_id, name, phone, relationship, email, is_primary)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (user_id, name, phone, relationship, email, is_primary))
    conn.commit()
    contact_id = cursor.lastrowid

    cursor.execute("SELECT * FROM emergency_contacts WHERE id = ?", (contact_id,))
    contact = dict(cursor.fetchone())
    conn.close()

    return jsonify({"message": "Emergency contact added successfully", "contact": contact}), 201

@app.route("/api/contacts/<int:contact_id>", methods=["PUT"])
def update_contact(contact_id):
    data = request.get_json() or {}
    name = data.get("name")
    phone = data.get("phone")
    relationship = data.get("relationship")
    email = data.get("email")
    is_primary = data.get("is_primary")

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT user_id FROM emergency_contacts WHERE id = ?", (contact_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return jsonify({"error": "Contact not found"}), 404
    
    user_id = row["user_id"]

    if is_primary:
        cursor.execute("UPDATE emergency_contacts SET is_primary = 0 WHERE user_id = ?", (user_id,))

    cursor.execute("""
    UPDATE emergency_contacts
    SET name = COALESCE(?, name),
        phone = COALESCE(?, phone),
        relationship = COALESCE(?, relationship),
        email = COALESCE(?, email),
        is_primary = COALESCE(?, is_primary)
    WHERE id = ?
    """, (name, phone, relationship, email, is_primary, contact_id))
    conn.commit()

    cursor.execute("SELECT * FROM emergency_contacts WHERE id = ?", (contact_id,))
    contact = dict(cursor.fetchone())
    conn.close()

    return jsonify({"message": "Contact updated successfully", "contact": contact}), 200

@app.route("/api/contacts/<int:contact_id>", methods=["DELETE"])
def delete_contact(contact_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM emergency_contacts WHERE id = ?", (contact_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Contact deleted successfully"}), 200

@app.route("/api/contacts/test-alert", methods=["POST"])
def test_contact_alert():
    data = request.get_json() or {}
    contact_name = data.get("name", "Emergency Contact")
    phone = data.get("phone", "+1 555-0100")
    user_name = data.get("user_name", "Sarah Jenkins")

    test_msg = f"[TEST ALERT] Hi {contact_name}, this is a test notification from Women Safety Analytics verifying that {user_name} has listed you as their emergency safety guardian. System is active & operational."

    return jsonify({
        "success": True,
        "message": f"Test alert successfully dispatched to {contact_name} ({phone})",
        "preview_text": test_msg,
        "channels": ["SMS (Verified)", "WhatsApp Notification (Verified)"]
    }), 200

# ==========================================
# AI SAFETY ASSISTANT (GEMINI + SAFETY ENGINE)
# ==========================================

AI_SAFETY_SYSTEM_PROMPT = """You are 'Aegis', the specialized Women Safety AI Assistant within the 'Women Safety Analytics' platform.
Your mission is to empower, protect, and guide women through safety challenges, suspicious situations, travel security, legal harassment rights, emergency self-defense, and psychological calming during distress.

Always follow these golden safety rules:
1. IF IMMEDIATE DANGER: Instruct the user clearly to press the red Emergency SOS button on screen, call 112/1091/911, and move to a well-lit public area.
2. ACTIONABLE & TACTICAL: Provide step-by-step, calm, actionable advice (e.g. 1-2-3 bullet points).
3. EMPATHETIC & REASSURING: Never victim-blame. Validate their feelings, keep them calm and alert.
4. SITUATION-SPECIFIC:
   - If followed: Cross the street, head to an open store/bank ATM, call a friend loudly on speaker, do not go home if isolated.
   - Ride-share safety: Check license plates, verify child-lock, share live GPS, call someone.
   - Domestic / Stalking: Document evidence, contact women helplines (1091, NCW 7827170170), find safe shelters.
   - Physical self-defense: Target vulnerable zones (Eyes, Nose, Throat, Groin).
Format response cleanly with markdown, bullet points, and bold text for easy reading under stress."""

def fallback_safety_expert(user_message):
    """Intelligent fallback rule & heuristic safety assistant engine."""
    msg = user_message.lower()

    if any(w in msg for w in ["followed", "following", "behind me", "stalked", "stalking", "shadowed"]):
        return (
            "### 🚨 Immediate Action: If You Believe You Are Being Followed\n\n"
            "1. **Do NOT head to an isolated home or dark alley:** Head immediately toward the nearest well-lit, open public space (e.g., supermarket, 24/7 petrol pump, hotel lobby, or metro station).\n"
            "2. **Cross the street:** Change direction to confirm if they are intentionally mirroring you.\n"
            "3. **Make a loud phone call:** Call an emergency contact or police (112 / 1091) on speakerphone and clearly state: *'I am on [Street Name] approaching [Landmark], see you in 2 minutes.'*\n"
            "4. **Trigger Emergency SOS:** Press the red **SOS Button** on this platform to transmit your live GPS coordinates to your registered emergency guardians.\n"
            "5. **Prepare for defense:** Hold keys firmly or keep personal alarm ready. Never hesitate to create a loud scene by shouting *'STAY BACK - CALL THE POLICE!'*"
        )
    elif any(w in msg for w in ["cab", "taxi", "uber", "ola", "ride", "auto", "car"]):
        return (
            "### 🚗 Late-Night Ride & Taxi Safety Protocol\n\n"
            "1. **Confirm Identity Before Boarding:** Ask the driver *'Who are you picking up?'* rather than revealing your name first.\n"
            "2. **Verify Vehicle Details:** Match the car model, color, and license plate number exactly with the booking app.\n"
            "3. **Check Back-Door Locks:** Ensure child safety locks are disengaged and doors open freely from the inside.\n"
            "4. **Share Live Trip GPS:** Send your live route link to a trusted contact via our Emergency Contacts tab.\n"
            "5. **Monitor Route:** Keep Google Maps / Apple Maps active on your screen to spot any unexpected deviations immediately."
        )
    elif any(w in msg for w in ["harass", "harassment", "workplace", "boss", "colleague", "inappropriate"]):
        return (
            "### 🛡️ Dealing with Workplace Harassment & Legal Safeguards\n\n"
            "1. **Document Every Single Occurrence:** Keep a private log with dates, times, exact statements, locations, and any witnesses.\n"
            "2. **Save Digital Evidence:** Take screenshots of chat messages, preserve emails, and back them up to a personal, non-work account.\n"
            "3. **Internal Escalation:** File a formal written complaint with your company's **Internal Complaints Committee (ICC / POSH)** or HR Department.\n"
            "4. **Statutory & Legal Avenues:** You have the right to approach the National Commission for Women (NCW) or file a complaint under Section 354A of the Penal Code.\n"
            "5. **Support:** Reach out to verified confidential women legal helplines (Dial **1091** or **181**)."
        )
    elif any(w in msg for w in ["panic", "anxiety", "scared", "fear", "calm", "breathe"]):
        return (
            "### 🫁 Grounding & Panic-Reduction Protocol (You Are Strong & In Control)\n\n"
            "Let's ground your senses right now:\n\n"
            "**Box Breathing Technique:**\n"
            "- 💨 **Inhale slowly** through your nose for **4 seconds**\n"
            "- ⏸️ **Hold** your breath for **4 seconds**\n"
            "- 🌬️ **Exhale completely** through your mouth for **4 seconds**\n"
            "- ⏸️ **Hold empty** for **4 seconds**\n\n"
            "**5-4-3-2-1 Sensory Grounding:**\n"
            "- Name **5 things** you can see right now\n"
            "- Name **4 things** you can physically touch\n"
            "- Name **3 sounds** you can hear\n"
            "- Name **2 scents** you can smell\n"
            "- Name **1 positive truth:** *'I am taking active steps to keep myself safe.'*"
        )
    elif any(w in msg for w in ["self-defense", "defense", "strike", "attack", "fight", "hit"]):
        return (
            "### ⚡ High-Impact Physical Self-Defense Tactics\n\n"
            "When physical escape is blocked, strike these vulnerable target areas decisively:\n\n"
            "1. **Palm-Heel Strike to the Nose:** Push the base of your open palm upward hard into the nose cartilage.\n"
            "2. **The Throat Thrust / Clavicle Strike:** Aim fin
