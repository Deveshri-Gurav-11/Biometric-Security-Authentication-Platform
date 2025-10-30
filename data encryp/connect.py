from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/receive-email', methods=['POST'])
def receive_email():
    try:
        # Parse incoming email data (depends on the provider)
        sender = request.form.get('from')  # Sender's email address
        recipient = request.form.get('to')  # Recipient's email address
        subject = request.form.get('subject')  # Email subject
        body = request.form.get('text')  # Email body (plain text)

        # Print or process the email data
        print(f"Email received:\nFrom: {sender}\nTo: {recipient}\nSubject: {subject}\nBody:\n{body}")

        # Return a success response
        return jsonify({"message": "Email received successfully!"}), 200

    except Exception as e:
        print(f"Error receiving email: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
