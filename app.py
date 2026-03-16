import os
import requests
from flask import Flask, render_template, request
from twilio.rest import Client
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)
app.secret_key = "secret_key_123"

# ლიმიტი: 1 IP-დან საათში მაქსიმუმ 10 მესიჯი
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["10 per hour"]
)

# მონაცემები Render-ის Environment Variables-იდან წამოვა
ACCOUNT_SID = os.environ.get('TWILIO_SID')
AUTH_TOKEN = os.environ.get('TWILIO_TOKEN')
TWILIO_NUMBER = os.environ.get('TWILIO_NUMBER')
RECAPTCHA_SITE_KEY = os.environ.get('RECAPTCHA_SITE_KEY')
RECAPTCHA_SECRET_KEY = os.environ.get('RECAPTCHA_SECRET_KEY')

client = Client(ACCOUNT_SID, AUTH_TOKEN) if ACCOUNT_SID and AUTH_TOKEN else None

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ka">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Anonymous SMS - გაგზავნე ანონიმურად</title>
    <script src="https://www.google.com/recaptcha/api.js" async defer></script>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background-color: #0f172a; color: #f8fafc; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; padding: 20px; }
        .container { background-color: #1e293b; padding: 30px; border-radius: 16px; box-shadow: 0 10px 25px rgba(0,0,0,0.3); width: 100%; max-width: 400px; border: 1px solid #334155; }
        h2 { text-align: center; color: #38bdf8; margin-bottom: 25px; }
        .input-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 8px; font-size: 14px; color: #94a3b8; }
        input, textarea { width: 100%; padding: 12px; border-radius: 8px; border: 1px solid #334155; background-color: #0f172a; color: white; box-sizing: border-box; outline: none; transition: 0.3s; }
        input:focus, textarea:focus { border-color: #38bdf8; }
        button.send-btn { width: 100%; padding: 14px; background-color: #38bdf8; border: none; border-radius: 8px; color: #0f172a; font-weight: bold; font-size: 16px; cursor: pointer; transition: 0.3s; margin-top: 10px; }
        button.send-btn:hover { background-color: #0ea5e9; }
        .support-box { margin-top: 25px; padding: 15px; background-color: #0f172a; border-radius: 12px; border: 1px dashed #38bdf8; }
        .iban-container { display: flex; align-items: center; background: #1e293b; padding: 8px; margin-top: 8px; border-radius: 6px; justify-content: space-between; }
        .iban-text { font-size: 11px; color: #38bdf8; font-family: monospace; }
        .copy-btn { background: #38bdf8; border: none; color: #0f172a; padding: 5px 10px; border-radius: 4px; font-size: 10px; cursor: pointer; font-weight: bold; }
        .rules { margin-top: 20px; font-size: 11px; color: #64748b; text-align: center; border-top: 1px solid #334155; padding-top: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <h2>Anonymous SMS</h2>
        <form action="/send-sms" method="POST">
            <div class="input-group">
                <label>მიმღების ნომერი</label>
                <input type="text" name="phone" placeholder="+995 5xx xx xx xx" required>
            </div>
            <div class="input-group">
                <label>შეტყობინება</label>
                <textarea name="message" rows="4" placeholder="დაწერე რამე..." required></textarea>
            </div>

            <div class="g-recaptcha" data-sitekey="''' + (RECAPTCHA_SITE_KEY or "") + '''" style="margin-bottom: 15px;"></div>

            <button type="submit" class="send-btn">გაგზავნა</button>
        </form>

        <div class="support-box">
            <p style="margin: 0 0 8px 0; font-size: 13px; color: #38bdf8; font-weight: bold; text-align: center;">🧡 მხარდაჭერა</p>
            <div style="font-size: 12px; color: #cbd5e1;">
                <b>მიმღები:</b> გ.ა <br>
                <b>ბანკი:</b> საქართველოს ბანკი
                <div class="iban-container">
                    <span class="iban-text" id="iban">GE38BG0000000581620953</span>
                    <button class="copy-btn" onclick="copyIBAN()">COPY</button>
                </div>
            </div>
        </div>

        <div class="rules">სპამი და მუქარა ისჯება კანონით.</div>
    </div>
    <script>
        function copyIBAN() {
            const iban = document.getElementById('iban').innerText;
            navigator.clipboard.writeText(iban);
            alert('ანგარიში დაკოპირდა!');
        }
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return HTML_TEMPLATE

@app.route('/send-sms', methods=['POST'])
def send_sms():
    recaptcha_response = request.form.get('g-recaptcha-response')
    verify_response = requests.post(
        'https://www.google.com/recaptcha/api/siteverify',
        data={'secret': RECAPTCHA_SECRET_KEY, 'response': recaptcha_response}
    ).json()

    if not verify_response.get('success'):
        return "<h3>გთხოვთ დაადასტუროთ, რომ რობოტი არ ხართ!</h3><a href='/'>უკან</a>"

    target_phone = request.form.get('phone')
    message_body = request.form.get('message')

    if not client:
        return "<h3>სერვერის შეცდომა: Twilio კონფიგურაცია აკლია.</h3>"

    try:
        client.messages.create(body=message_body, from_=TWILIO_NUMBER, to=target_phone)
        return "<h3>წარმატებით გაიგზავნა!</h3><a href='/'>უკან</a>"
    except Exception as e:
        return f"<h3>შეცდომა: {str(e)}</h3><a href='/'>უკან</a>"

if __name__ == '__main__':
    app.run(debug=True)
