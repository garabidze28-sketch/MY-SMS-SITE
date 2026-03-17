import os
from flask import Flask, render_template_string, request
from twilio.rest import Client

app = Flask(__name__)

# Twilio მონაცემები Render-ის Environment Variables-იდან
TWILIO_SID = os.environ.get('TWILIO_SID')
TWILIO_TOKEN = os.environ.get('TWILIO_TOKEN')
TWILIO_NUMBER = os.environ.get('TWILIO_NUMBER')

# Twilio-ს ინიციალიზაცია
client = Client(TWILIO_SID, TWILIO_TOKEN) if TWILIO_SID and TWILIO_TOKEN else None

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ka">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SMISSY.ge - ანონიმური მესიჯები</title>
    <style>
        :root { --main-red: #e11d48; --bg: #ffffff; }
        body { font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; background-color: var(--bg); margin: 0; padding: 0; overflow-x: hidden; }
        header { background: var(--main-red); padding: 15px 20px; display: flex; justify-content: space-between; align-items: center; color: white; position: sticky; top: 0; z-index: 1000; }
        .logo { font-size: 24px; font-weight: bold; letter-spacing: 1px; }
        .container { max-width: 480px; margin: 0 auto; padding: 20px; position: relative; }
        .heart { position: absolute; color: #ff4d4d; font-size: 18px; user-select: none; z-index: 1; animation: float 4s infinite ease-in-out; opacity: 0.8; }
        @keyframes float { 0% { transform: translateY(0); opacity: 0.8; } 50% { transform: translateY(-20px); opacity: 1; } 100% { transform: translateY(0); opacity: 0.8; } }
        .card { border: 1px solid #eee; border-radius: 10px; padding: 20px; background: white; margin-bottom: 20px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
        label { display: block; margin-bottom: 8px; font-weight: bold; font-size: 14px; color: #333; text-align: left; }
        input[type="text"], textarea { width: 100%; padding: 12px; margin-bottom: 20px; border: 1px solid #ccc; border-radius: 8px; box-sizing: border-box; font-size: 16px; }
        .bank-container { border: 1px solid #ccc; border-radius: 12px; padding: 15px; margin-bottom: 20px; text-align: left; }
        .bank-card { border: 2px solid #333; border-radius: 12px; padding: 12px; display: flex; align-items: center; gap: 12px; cursor: pointer; background: #fff; }
        .bank-logo { width: 40px; height: 40px; }
        .iban-text { font-family: monospace; font-size: 14px; font-weight: bold; color: #000; }
        .terms-container { display: flex; align-items: center; gap: 10px; margin-bottom: 20px; font-size: 14px; color: #555; text-align: left; }
        .btn-send { width: 100%; background: #fff; border: 1px solid #ccc; padding: 16px; border-radius: 8px; font-size: 16px; cursor: pointer; font-weight: bold; }
        .rule-card { border: 1px solid #eee; border-radius: 8px; padding: 15px; margin-bottom: 10px; text-align: left; }
    </style>
</head>
<body>
<header><div class="logo">SMISSY</div><div style="font-size: 24px;">☰</div></header>
<div class="container">
    <div class="card">
        <h3>ანონიმური მესიჯები 2 ლარად</h3>
        <p>მესიჯი ადრესატთან მივა მომენტალურად!</p>
    </div>
    <form action="/send-sms-now" method="POST">
        <label>მიმღების ნომერი</label>
        <input type="text" name="phone" placeholder="მაგ: +995599XXXXXX" required>
        <label>შეტყობინება</label>
        <textarea name="message" rows="4" placeholder="English only..." required></textarea>
        <div class="bank-container">
            <div class="bank-card" onclick="copyIban()">
                <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/1/15/Bank_of_Georgia_logo.svg/1024px-Bank_of_Georgia_logo.svg.png" class="bank-logo">
                <div><div class="iban-text">GE38BG0000000581620953</div><div style="font-size: 12px;">გ.ა</div></div>
            </div>
        </div>
        <div class="terms-container">
            <input type="checkbox" required> <span>ვეთანხმები წესებს</span>
        </div>
        <button type="submit" class="btn-send">გაგზავნა</button>
    </form>
</div>
<script>
    function copyIban() { navigator.clipboard.writeText("GE38BG0000000581620953"); alert("კოპირებულია!"); }
</script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/send-sms-now', methods=['POST'])
def send_sms_now():
    phone = request.form.get('phone')
    msg = request.form.get('message')
    if not client:
        return "<h2>ერორი: Twilio-ს მონაცემები Render-ზე არ არის!</h2>"
    try:
        client.messages.create(body=msg, from_=TWILIO_NUMBER, to=phone)
        return "<h2>✅ გაიგზავნა!</h2><a href='/'>უკან</a>"
    except Exception as e:
        return f"<h2>❌ ვერ გაიგზავნა: {str(e)}</h2><a href='/'>უკან</a>"

if __name__ == '__main__':
    app.run(debug=True)
