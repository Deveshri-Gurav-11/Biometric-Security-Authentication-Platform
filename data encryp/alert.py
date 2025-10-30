import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time
import os

def send_email(subject, body, recipient_email, sender_email, sender_password):
    try:
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP('smtp.gmail.com', 587)  # Replace with your SMTP server
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient_email, msg.as_string())
        server.quit()
        print("Email sent successfully.")
    except Exception as e:
        print(f"Failed to send email: {e}")

def monitor_logs(log_file, trigger_text):
    try:
        with open(log_file, 'r') as f:
            f.seek(0, os.SEEK_END)  # Start at the end of the file
            while True:
                line = f.readline()
                if not line:
                    time.sleep(1)  # Wait for new lines
                    continue
                if trigger_text in line:
                    send_email(
                        subject="Unauthorized Access Attempt Detected",
                        body=f"Suspicious activity detected in log: {line}",
                        recipient_email="deveshrigurav.com",
                        sender_email="your_email@example.com",
                        sender_password="your_email_password"
                    )
    except FileNotFoundError:
        print(f"Log file {log_file} not found. Please check the path.")

if __name__ == "__main__":
    app.run(debug=True)