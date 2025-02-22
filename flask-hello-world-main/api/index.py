import io
import smtplib
import os
from flask import Flask, request, send_file
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

app = Flask(__name__)

# Load email credentials from environment variables
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587

# Tracking pixel (1x1 transparent PNG)
TRACKING_PIXEL = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\x0eIDATx\x9cc\x62\x60\x60\x60\x00\x00\x00\x04\x00\x01\xf4\xce\x0f\x0e\x00\x00\x00\x00IEND\xaeB`\x82'

@app.route('/')
def home():
    """Homepage to confirm the service is running."""
    return "✅ Tracking Pixel Service is Running!"

@app.route('/pixel.png')
def tracking_pixel():
    """Serves a tracking pixel and logs email opens only when the pixel is requested."""
    print(f"📩 Email opened by: {request.remote_addr}")
    return send_file(io.BytesIO(TRACKING_PIXEL), mimetype='image/png')

def send_email_with_tracking(recipient_email):
    """Sends an email with a tracking pixel."""
    if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
        print("❌ Email credentials are missing. Check environment variables.")
        return

    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = recipient_email
        msg['Subject'] = 'Tracked Email'

        # Use your Vercel-deployed URL here
        vercel_tracking_url = "https://flask-hello-world-henna-gamma.vercel.app/pixel.png"
        html = f"""
        <html>
          <body>
            <p>Hello, this email contains a tracking pixel.</p>
            <img src="{vercel_tracking_url}" alt="" style="display:none;" />
          </body>
        </html>
        """
        msg.attach(MIMEText(html, 'html'))

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.sendmail(EMAIL_ADDRESS, recipient_email, msg.as_string())

        print(f"✅ Email sent successfully to {recipient_email} with tracking pixel.")

    except Exception as e:
        print(f"❌ Error sending email: {e}")

@app.route('/send-email/<recipient_email>')
def trigger_email(recipient_email):
    """Trigger sending an email with a tracking pixel."""
    send_email_with_tracking(recipient_email)
    return f"✅ Email sent to {recipient_email}"

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080)
