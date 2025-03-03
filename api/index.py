import io
import smtplib
import os
import threading
from flask import Flask, request, send_file, jsonify
import uuid
from database import Database
import socket
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

app = Flask(__name__)
database = Database('mail_data.db')
database.init_database()
database.create_schema()



# Load email credentials from environment variables
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587

# Tracking pixel (1x1 transparent PNG)
TRACKING_PIXEL = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\x0eIDATx\x9cc\x62\x60\x60\x60\x00\x00\x00\x04\x00\x01\xf4\xce\x0f\x0e\x00\x00\x00\x00IEND\xaeB`\x82'

print(EMAIL_ADDRESS, EMAIL_PASSWORD)

@app.route('/')
def home():
    return "✅ Tracking Pixel Service is Running!"


def get_ip_address():
    sock = socket.socket()
    sock.connect(('1.1.1.1', 80))
    return sock.getsockname()[0]

IP_ADDRESS = 'akashsinghlalla.pythonanywhere.com'
print("IP ADDRESS : ", IP_ADDRESS)
@app.route('/pixel.png')
def tracking_pixel():
    recipient_email = request.args.get("email")
    try:
        recipient_uuid = uuid.UUID(request.args.get("user"))
    except:
        print("Error while parsing uuid")
        recipient_uuid = uuid.uuid4()
    print(f"📩 Email opened by: {recipient_email}")
    database.update_user_time(recipient_uuid)
    return send_file(io.BytesIO(TRACKING_PIXEL), mimetype='image/png')

def send_email_with_tracking(recipient_email):

    email_uuid = uuid.uuid4()
    """Sends an email with a tracking pixel."""
    if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
        print("❌ Email credentials are missing. Check environment variables.")
        return

    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = recipient_email
        msg['Subject'] = 'Tracked Email'

        # Tracking pixel URL
        vercel_tracking_url = f"http://{IP_ADDRESS}/pixel.png?email={recipient_email}?user={email_uuid}"
        html = f"""
        <html>
          <body>
            <p>Hello, this side Akash singh lalla.</p>
            <img src="{vercel_tracking_url}" alt="" style="display:none;" />
          </body>
        </html>
        """
        print(html)
        msg.attach(MIMEText(html, 'html'))

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.sendmail(EMAIL_ADDRESS, recipient_email, msg.as_string())

        database.insert_email_recipient(email_uuid, recipient_email)
        print(f"✅ Email sent successfully to {recipient_email} with tracking pixel.")
        

    except Exception as e:
        print(f"❌ Error sending email to {recipient_email}: {e}")

@app.route('/send-email/<path:emails>')
def send_multiple_emails(emails):
    """Send emails to multiple recipients using a URL path format."""
    recipient_emails = emails.split("/")  # Split emails by '/'
    
    if not recipient_emails:
        return jsonify({"error": "No email addresses provided"}), 400

    threads = []
    for email in recipient_emails:
        send_email_with_tracking(email)
        # thread = threading.Thread(target=send_email_with_tracking, args=(email,))
        # threads.append(thread)
        # thread.start()

    for thread in threads:
        thread.join()

    return jsonify({"message": f"✅ Emails sent to {len(recipient_emails)} recipients."})

# if __name__ == '__main__':
#     app.run(host=IP_ADDRESS, port=80)
