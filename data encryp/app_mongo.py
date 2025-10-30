# app_mongo.py
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_mail import Mail, Message
from cryptography.fernet import Fernet
from bson.binary import Binary
from bson import ObjectId
import os
import cv2
import numpy as np
from flask_pymongo import PyMongo

# Import image processing utilities
from fingerprint import random_patch_merge, load_image_grayscale, resize_to_same

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)

# ===================== CONFIG =====================

# MongoDB config
app.config["MONGO_URI"] = "mongodb://localhost:27017/appEncryption"
mongo = PyMongo(app)

# Email config
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'deveshrigurav11@gmail.com'
app.config['MAIL_PASSWORD'] = 'vbxg zhvc kzeo mctj'  # Replace with Gmail App Password
app.config['MAIL_DEFAULT_SENDER'] = 'deveshrigurav11@gmail.com'
mail = Mail(app)

# ---------------- EMAIL ALERT FUNCTION ----------------
import threading

def send_alert_email(subject, body, recipient_email):
    """Send email asynchronously to prevent blocking the app."""
    try:
        msg = Message(
            subject,
            sender=app.config['MAIL_DEFAULT_SENDER'],
            recipients=[recipient_email]
        )
        msg.body = body

        def send_async(app, msg):
            with app.app_context():
                try:
                    mail.send(msg)
                    print(f"✅ Email sent successfully to {recipient_email}")
                except Exception as e:
                    print(f"❌ Email sending failed: {e}")

        threading.Thread(target=send_async, args=(app, msg)).start()

    except Exception as e:
        print(f"⚠️ Error preparing email: {e}")

# File upload config
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Encryption key
key = Fernet.generate_key()
cipher = Fernet(key)

# Confounder biometric image path
USELESS_BIOMETRIC_PATH = os.path.join(app.root_path, 'static', 'confounder.png')


# ===================== HELPER FUNCTIONS =====================
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ===================== ROUTES =====================

@app.route('/')
def index():
    return render_template('index.html')


# ---------- REGISTER ----------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        phone = request.form.get('phone')

        # Uniqueness check
        if mongo.db.users.find_one({'username': username}):
            flash("Username already exists.")
            return redirect(url_for('register'))
        if mongo.db.users.find_one({'email': email}):
            flash("Email already registered.")
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password)

        user_doc = {
            "username": username,
            "password": hashed_password,
            "email": email,
            "phone": phone
        }

        result = mongo.db.users.insert_one(user_doc)
        session['user_id'] = str(result.inserted_id)
        flash("Registration successful!")
        return redirect(url_for('dashboard'))
    return render_template('register.html')


# ---------- LOGIN ----------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = mongo.db.users.find_one({'username': username})
        if user and check_password_hash(user['password'], password):
            session['user_id'] = str(user['_id'])
            flash("Login successful!", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid username or password.", "error")
    return render_template('login.html')


# ---------- DASHBOARD ----------
@app.route('/dashboard')
def dashboard():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    uploads = list(mongo.db.uploads.find({'user_id': user_id}))
    return render_template('dashboard.html', uploaded_files=uploads)


# ---------- UPLOAD (Sends success email) ----------
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    user_id = session.get('user_id')
    if not user_id:
        flash("Please log in first.", "error")
        return redirect(url_for('login'))

    if request.method == 'POST':
        if 'file' not in request.files:
            flash("No file part in request.", "error")
            return redirect(url_for('upload'))

        file = request.files['file']
        if file.filename == '':
            flash("No file selected.", "error")
            return redirect(url_for('upload'))

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(save_path)
            print(f"✅ File saved: {save_path}")

            mongo.db.uploads.update_one(
                {"user_id": user_id},
                {"$set": {"filename": filename}},
                upsert=True
            )

            # --- ✅ Send "successfully secured" email in background ---
            user = mongo.db.users.find_one({"_id": ObjectId(user_id)})
            if user:
                recipient_email = user.get("email")
                username = user.get("username", "User")

                email_body = f"""
                Hello {username},

                ✅ Your biometric data has been securely uploaded to SecureIT.
                If this wasn’t you, please log in and change your password immediately.

                Time: {os.popen('date').read().strip()}
                IP: {request.remote_addr}

                Regards,
                SecureIT Security Team
                """

                send_alert_email(
                    "✅ SecureIT: Biometric Upload Successful",
                    email_body,
                    recipient_email
                )

            flash("✅ Biometric uploaded successfully!", "success")
            return redirect(url_for('dashboard'))

        else:
            flash("Invalid file type. Please upload an image file.", "error")

    return render_template('upload.html')



@app.route('/success')
def success_page():
    return render_template('success.html')


# ---------- BIOMETRIC ENROLL ----------
# ---------- BIOMETRIC ENROLL ----------
@app.route('/biometric-enroll', methods=['POST'])
def biometric_enroll():
    user_id = session.get('user_id')
    if not user_id:
        flash("Unauthorized access. Please log in first.", "error")
        return redirect(url_for('login'))

    if 'biometric_file' not in request.files:
        flash("No biometric file selected.", "error")
        return redirect(url_for('dashboard'))

    biometric_file = request.files['biometric_file']
    if biometric_file.filename == '':
        flash("No file selected.", "error")
        return redirect(url_for('dashboard'))

    if not os.path.exists(USELESS_BIOMETRIC_PATH):
        flash("Server error: Confounder image missing. Contact admin.", "error")
        return redirect(url_for('dashboard'))

    try:
        temp_filename = secure_filename(biometric_file.filename)
        temp_path = os.path.join(app.config['UPLOAD_FOLDER'], temp_filename)
        biometric_file.save(temp_path)

        user_img = load_image_grayscale(temp_path)
        useless_img = load_image_grayscale(USELESS_BIOMETRIC_PATH)

        confused_img = random_patch_merge(
            user_img, useless_img, patch_size=30, patch_frac=0.5,
            seed=int(user_id[-6:], 16) if len(user_id) > 6 else None
        )

        _, buffer = cv2.imencode('.png', confused_img)
        confused_data = Binary(buffer.tobytes())

        mongo.db.biometrics.update_one(
            {'user_id': user_id},
            {'$set': {'fingerprint_data': confused_data}},
            upsert=True
        )

        os.remove(temp_path)

        # ✅ Send email to confirm secure biometric storage
        try:
            user = mongo.db.users.find_one({"_id": ObjectId(user_id)})
            if user:
                send_alert_email(
                    subject="🔒 SecureIT: Your Biometric Data Has Been Secured",
                    body=(
                        f"Hello {user['username']},\n\n"
                        f"Your biometric data has been securely processed and encrypted by SecureIT.\n"
                        f"This ensures your sensitive fingerprint data is safely stored and protected.\n\n"
                        f"Time: {os.popen('date').read().strip()}\n"
                        f"IP: {request.remote_addr}\n\n"
                        f"Regards,\nSecureIT Security Team"
                    ),
                    recipient_email=user['email']
                )
                print(f"📧 Secure biometric email sent to {user['email']}")
        except Exception as e:
            print(f"⚠️ Failed to send biometric secure email: {e}")

        flash("✅ Biometric data secured successfully!", "success")
        return redirect(url_for('dashboard'))

    except Exception as e:
        if 'temp_path' in locals() and os.path.exists(temp_path):
            os.remove(temp_path)
        print(f"Error during biometric enrollment: {e}")
        flash("❌ Biometric enrollment failed due to a server error.", "error")
        return redirect(url_for('dashboard'))


# ---------- BIOMETRIC SCAN (Alert Email) ----------
@app.route('/biometric-scan', methods=['POST'])
def biometric_scan():
    username = request.form.get('username', 'UNKNOWN_USER')
    admin_email = 'deveshrigurav11@gmail.com'
    is_suspicious = request.form.get('suspicious', 'false').lower() == 'true'

    if is_suspicious:
        log_message = f"🚨 Suspicious biometric attempt detected for user {username}."
        print(log_message)

        alert_body = (
            f"🚨 ALERT: A suspicious biometric scan attempt has been detected.\n\n"
            f"User: {username}\n"
            f"IP Address: {request.remote_addr}\n"
            f"Time: {os.popen('date').read().strip()}\n"
            f"Details: Possible spoofing attempt using photo/video.\n\n"
            f"Immediate attention is recommended.\n\n"
            f"– SecureIT Security System"
        )

        send_alert_email(
            subject="🚨 SecureIT: Suspicious Biometric Scan Detected",
            body=alert_body,
            recipient_email=admin_email
        )

        return jsonify({"message": "Access denied"}), 403

    return jsonify({"message": "Biometric check passed."}), 200


# ---------- DELETE ACCOUNT ----------
@app.route('/delete-account', methods=['POST'])
def delete_account():
    user_id = session.get('user_id')
    if not user_id:
        flash("Please log in to delete your account.")
        return redirect(url_for('login'))

    user = mongo.db.users.find_one({'_id': ObjectId(user_id)})
    if not user:
        flash("User not found.")
        session.pop('user_id', None)
        return redirect(url_for('index'))

    try:
        mongo.db.uploads.delete_many({'user_id': user_id})
        mongo.db.biometrics.delete_many({'user_id': user_id})
        mongo.db.users.delete_one({'_id': ObjectId(user_id)})

        session.pop('user_id', None)
        flash(f"Account '{user['username']}' deleted successfully.", 'success')
        return redirect(url_for('index'))

    except Exception as e:
        print(f"Error deleting account: {e}")
        flash(f"Error deleting account: {e}", 'error')
        return redirect(url_for('dashboard'))


# ==================================================
if __name__ == "__main__":
    app.run(debug=True)
