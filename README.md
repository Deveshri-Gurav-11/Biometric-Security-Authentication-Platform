# 🔐 Biometric Security Authentication Platform

SecureIT is a Flask-based biometric security system designed to securely upload, encrypt, and manage biometric data such as fingerprints while monitoring suspicious access attempts. The platform combines biometric storage, encryption techniques, database integration, and real-time alert mechanisms to provide a secure authentication environment.

The project demonstrates practical implementation of security concepts, computer vision, database operations, and backend development.

---

## 🚀 Features

- 🔑 Secure fingerprint upload and storage
- 🔒 Encryption of biometric information
- 👆 Fingerprint data management
- 📧 Real-time email alerts using Flask-Mail
- 🗄 MongoDB database integration
- 🖼 Biometric image processing with OpenCV
- 🚨 Detection and monitoring of suspicious access attempts
- 🌐 Flask-powered web interface

---

## 🛠 Tech Stack

### Backend
- Flask
- Python

### Database
- MongoDB

### Libraries & Tools
- OpenCV
- Flask-Mail
- PyMongo
- HTML/CSS
- Encryption utilities

---

## 📂 Project Structure

```bash
Biometric-Security-Authentication-Platform/
│
├── static/
│   └── uploads/
│       ├── finger_1.jpg
│       └── finger_2.jpg
│
├── templates/                 # HTML templates
│
├── 1.py                       # Application utilities
├── alert.py                   # Email alert handling
├── app_mongo.py               # Main Flask application
├── connect.py                 # Database connection setup
├── create_db_mongo.py         # Database creation
├── delete_data.py             # Data deletion utilities
├── fingerprint.py             # Fingerprint processing logic
│
├── README.md
```

---

## ⚙️ Installation & Setup

### Clone repository

```bash
git clone https://github.com/Deveshri-Gurav-11/Biometric-Security-Authentication-Platform.git
```

Move into project:

```bash
cd Biometric-Security-Authentication-Platform
```

---

### Install dependencies

```bash
pip install -r requirements.txt
```

---

### Configure Environment Variables

Create a `.env` file:

```env
MONGO_URI=your_mongodb_connection_string

MAIL_SERVER=your_mail_server
MAIL_PORT=your_mail_port

MAIL_USERNAME=your_email
MAIL_PASSWORD=your_password

SECRET_KEY=your_secret_key
```

---

### Run the application

```bash
python app_mongo.py
```

Application:

```bash
http://localhost:5000
```

---

## 🔄 Application Workflow

1. User uploads biometric fingerprint data
2. System processes the image using OpenCV
3. Sensitive information is encrypted
4. Data is stored securely in MongoDB
5. Authentication requests are monitored
6. Suspicious activity is detected
7. Email alerts are triggered automatically

---

## 🎯 Key Learning Outcomes

- Flask backend development
- MongoDB integration
- Biometric authentication concepts
- Image handling using OpenCV
- Email automation
- Data encryption practices
- Security-focused application design

---

## 🔮 Future Enhancements

- Face recognition support
- Multi-factor authentication
- User login system
- Admin dashboard
- Authentication history logs
- AI-based anomaly detection
- Cloud deployment

---

## 👩‍💻 Author

**Deveshri Gurav**

GitHub: https://github.com/Deveshri-Gurav-11

LinkedIn: https://www.linkedin.com/in/deveshri-gurav/

---

⭐ If you found this project useful, consider giving it a star.
