import os
import requests
from flask import Flask, render_template_string, request
from twilio.rest import Client

app = Flask(__name__)

# მონაცემები Render-ის Environment Variables-იდან
TWILIO_SID = os.environ.get('TWILIO_SID')
TWILIO_TOKEN = os.environ.get('TWILIO_TOKEN')
TWILIO_NUMBER = os.environ.get('TWILIO_NUMBER')
TG_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
TG_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

client = Client(TWILIO_SID, TWILIO_TOKEN) if TWILIO_SID and TWILIO_TOKEN else None

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ka">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GeoSMS - ანონიმური მესიჯები</title>
    <style>
        :root { --main-red: #e11d48; --dark: #111827; }
        body { font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; background: #f9fafb; margin: 0; overflow-x: hidden; }
        header { background: var(--main-red); padding: 15px 20px; color: white; display: flex; justify-content: space-between; align-items: center; font-weight: bold; font-size: 24px; position: sticky; top: 0; z-index: 1000; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .sidebar { position: fixed; top: 0; right: -280px; width: 280px; height: 100%; background: var(--dark); color: white; transition: 0.3s; z-index: 1001; padding: 25px; box-sizing: border-box; }
        .sidebar.active { right: 0; }
        .sidebar h3 { border-bottom: 1px solid #374151; padding-bottom: 10px; margin-bottom: 20px; color: var(--main-red); }
        .sidebar a { color: #cbd5e1; text-decoration: none; display: block; margin: 15px 0; font-size: 16px; }
        .container { max-width: 450px; margin: 0 auto; padding: 20px; position: relative; z-index: 1; }
        .heart { position: fixed; color: #ff4d4d; font-size: 20px; animation: float 6s infinite linear; opacity: 0; pointer-events: none; z-index: 0; }
        @keyframes float { 0% { transform: translateY(100vh) scale(0.5); opacity: 0; } 50% { opacity: 0.8; } 100% { transform: translateY(-10vh) scale(1.2); opacity: 0; } }
        .card { background: white; border-radius: 20px; padding: 25px; box-shadow: 0 10px 30px rgba(0,0,0,0.05); margin-bottom: 20px; border: 1px solid #f1f5f9; text-align: center; }
        label { display: block; text-align: left; margin-bottom: 8px; font-weight: 600; font-size: 14px; color: #374151; }
        input[type="text"], textarea, input[type="file"] { width: 100%; padding: 14px; border: 1px solid #e2e8f0; border-radius: 12px; box-sizing: border-box; font-size: 16px; margin-bottom: 15px; outline: none; }
        .bank-card { background: #fff; border: 2px solid #f1f5f9; border-radius: 15px; padding: 15px; display: flex; align-items: center; gap: 12px; cursor: pointer; transition: 0.2s; }
        .bank-logo { width: 45px; height: 45px; border-radius: 10px; background: #f97316; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; font-size: 10px; line-height: 1; text-align: center; }
        .iban { font-family: 'Courier New', monospace; font-weight: bold; color: #1e293b; font-size: 14px; word-break: break-all; }
        .btn-send { width: 100%; background: var(--main-red); color: white; border: none; padding: 18px; border-radius: 14px; font-size: 18px; font-weight: bold; cursor: pointer; box-shadow: 0 4px 15px rgba(225, 29, 72, 0.3); }
    </style>
</head>
<body>
<header><div>GeoSMS</div><div style="cursor:pointer; font-size: 28px;" onclick="toggleMenu()">☰</div></header>
<div class="sidebar" id="sidebar">
    <div style="text-align: right; cursor: pointer; font-size: 24px;" onclick="toggleMenu()">✕</div>
    <h3>მენიუ</h3>
    <a href="/">მთავარი</a>
    <a href="#" onclick="alert('Email: support@geosms.ge')">კონტაქტი</a>
</div>
<div class="container" id="heart-container">
    <div class="card">
        <h2 style="margin: 0; color: var(--main-red);">ანონიმური SMS</h2>
        <p style="color: #64748b; font-size: 15px;">მესიჯი 2 ლარად</p>
    </div>
    <form action="/submit" method="POST" enctype="multipart/form-data" class="card">
        <label>მიმღების ნომერი</label>
        <input type="text" name="phone" placeholder="5XXXXXXXX" required>
        <label>შეტყობინება (English Only)</label>
        <textarea name="message" rows="3" required></textarea>
        <label>გადახდა (BOG)</label>
        <div class="bank-card" onclick="navigator.clipboard.writeText('GE38BG0000000581620953'); alert('კოპირებულია!')">
            <div class="bank-logo">BANK OF<br>GEO</div>
            <div style="text-align: left;">
                <div class="iban">GE38BG0000000581620953</div>
                <div style="font-size: 11px; color: #f97316;">მიმღები: გ.ა</div>
            </div>
        </div>
        <label style="margin-top: 20px;">ატვირთე ჩეკი</label>
        <input type="file" name="receipt" accept="image/*" required>
        <button type="submit" class="btn-send">გაგზავნა</button>
    </form>
</div>
<script>
    function toggleMenu() { document.getElementById('sidebar').classList.toggle('active'); }
    setInterval(() => {
        const h = document.createElement('div');
        h.innerHTML = '❤️'; h.className = 'heart';
        h.style.left = Math.random() * 100 + 'vw';
        h.style.animationDuration = (Math.random() * 3 + 3) + 's';
        document.body.appendChild(h);
        setTimeout(() => h.remove(), 6000);
    }, 800);
</script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/submit', methods=['POST'])
def submit():
    phone = request.form.get('phone').replace(" ", "").replace("-", "")
    msg = request.form.get('message')
    receipt = request.files.get('receipt')

    # ნომრის ფორმატირება
    clean_phone = phone
    if not clean_phone.startswith('+'):
        if clean_phone.startswith('0'): clean_phone = clean_phone[1:]
        clean_phone = '+995' + clean_phone

    # 1. Telegram-ში გაგზავნა
    if TG_TOKEN and TG_CHAT_ID:
        try:
            receipt_data = receipt.read()
            tg_url = f"https://api.telegram.org/bot{TG_TOKEN}/sendPhoto"
            files = {'photo': ('receipt.jpg', receipt_data)}
            data = {'chat_id': TG_CHAT_ID, 'caption': f"🔔 ახალი შეკვეთა!\\n📱 ნომერი: {clean_phone}\\n💬 მესიჯი: {msg}"}
            requests.post(tg_url, data=data, files=files)
        except: pass

    # 2. Twilio SMS
    success = False
    status_text = ""
    if client:
        try:
            client.messages.create(body=f"GeoSMS: {msg}", from_=TWILIO_NUMBER, to=clean_phone)
            success = True
            status_text = "მესიჯი წარმატებით გაიგზავნა!"
        except Exception as e:
            status_text = f"შეცდომა: {str(e)}"
    else:
        status_text = "Twilio არ არის ჩართული"

    return f'<div style="text-align:center; padding:50px; font-family:sans-serif;"><h1>{"✅" if success else "❌"}</h1><h2>{status_text}</h2><a href="/">უკან</a></div>'

if __name__ == '__main__':
    app.run(debug=True)
