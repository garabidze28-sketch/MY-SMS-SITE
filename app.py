import os
import requests
from flask import Flask, render_template_string, request
from twilio.rest import Client

app = Flask(__name__)

# მონაცემები Render-იდან
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
        body { font-family: sans-serif; background: #f9fafb; margin: 0; overflow-x: hidden; text-align: center; }
        header { background: var(--main-red); padding: 20px; color: white; font-weight: bold; font-size: 24px; position: sticky; top: 0; z-index: 1000; }
        .container { max-width: 450px; margin: 20px auto; padding: 0 15px; }
        .card { background: white; border-radius: 20px; padding: 25px; box-shadow: 0 10px 30px rgba(0,0,0,0.05); margin-bottom: 20px; border: 1px solid #f1f5f9; }
        label { display: block; text-align: left; margin: 15px 0 5px; font-weight: bold; color: #374151; }
        input, textarea { width: 100%; padding: 15px; border: 1px solid #e2e8f0; border-radius: 12px; box-sizing: border-box; font-size: 16px; outline: none; }
        .bank-card { background: #fff; border: 2px solid #f1f5f9; border-radius: 15px; padding: 15px; display: flex; align-items: center; gap: 12px; cursor: pointer; }
        .bank-logo { width: 45px; height: 45px; border-radius: 10px; background: #f97316; display: flex; align-items: center; justify-content: center; color: white; font-size: 10px; font-weight: bold; }
        .btn-send { width: 100%; background: var(--main-red); color: white; border: none; padding: 20px; border-radius: 15px; font-size: 18px; font-weight: bold; cursor: pointer; margin-top: 20px; box-shadow: 0 4px 15px rgba(225, 29, 72, 0.3); }
        .heart { position: fixed; color: #ff4d4d; font-size: 20px; animation: float 6s infinite linear; opacity: 0; pointer-events: none; }
        @keyframes float { 0% { transform: translateY(100vh) scale(0.5); opacity: 0; } 50% { opacity: 0.8; } 100% { transform: translateY(-10vh) scale(1.2); opacity: 0; } }
    </style>
</head>
<body>
<header>GeoSMS</header>
<div class="container">
    <div class="card">
        <h2 style="margin:0; color:var(--main-red);">ანონიმური SMS</h2>
        <p style="color:#64748b;">გააგზავნე მესიჯი 2 ლარად</p>
    </div>
    <form action="/submit" method="POST" enctype="multipart/form-data" class="card">
        <label>მიმღების ნომერი</label>
        <input type="text" name="phone" placeholder="5XXXXXXXX" required>
        <label>შეტყობინება (English Only)</label>
        <textarea name="message" rows="3" required></textarea>
        <label>გადახდა (BOG)</label>
        <div class="bank-card" onclick="navigator.clipboard.writeText('GE38BG0000000581620953'); alert('კოპირებულია!')">
            <div class="bank-logo">BOG</div>
            <div style="text-align:left;">
                <div style="font-weight:bold; font-size:14px;">GE38BG0000000581620953</div>
                <div style="font-size:11px; color:#f97316;">მიმღები: გ.ა (დააჭირე კოპირებისთვის)</div>
            </div>
        </div>
        <label style="margin-top:20px;">ატვირთე ჩეკი</label>
        <input type="file" name="receipt" accept="image/*" required>
        <button type="submit" class="btn-send">გაგზავნა</button>
    </form>
</div>
<script>
    setInterval(() => {
        const h = document.createElement('div'); h.innerHTML = '❤️'; h.className = 'heart';
        h.style.left = Math.random() * 100 + 'vw'; h.style.animationDuration = (Math.random() * 3 + 3) + 's';
        document.body.appendChild(h); setTimeout(() => h.remove(), 6000);
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
    phone = request.form.get('phone', '').replace(" ", "").replace("-", "")
    msg = request.form.get('message', '')
    receipt = request.files.get('receipt')

    clean_phone = phone
    if not clean_phone.startswith('+'):
        if clean_phone.startswith('0'): clean_phone = clean_phone[1:]
        clean_phone = '+995' + clean_phone

    # --- TELEGRAM ---
    if TG_TOKEN and TG_CHAT_ID:
        try:
            img_data = receipt.read()
            receipt.seek(0)
            requests.post(f"https://api.telegram.org/bot{TG_TOKEN}/sendPhoto", 
                          data={'chat_id': TG_CHAT_ID, 'caption': f"🔔 ახალი SMS!\\n📱 ნომერი: {clean_phone}\\n💬 ტექსტი: {msg}"},
                          files={'photo': ('receipt.jpg', img_data)})
        except: pass

    # --- TWILIO ---
    success = False
    if client:
        try:
            client.messages.create(body=f"GeoSMS: {msg}", from_=TWILIO_NUMBER, to=clean_phone)
            success = True
        except: pass

    return f'''
    <div style="text-align:center; padding:50px; font-family:sans-serif;">
        <h1 style="font-size:60px;">{'✅' if success else '❌'}</h1>
        <h2>{'მესიჯი გაიგზავნა!' if success else 'SMS ვერ გაიგზავნა (Twilio Error)'}</h2>
        <p>ჩეკი მიღებულია და ადმინისტრაცია გადაამოწმებს.</p>
        <br><a href="/" style="color:#e11d48; font-weight:bold; text-decoration:none;">უკან დაბრუნება</a>
    </div>
    '''

if __name__ == '__main__':
    # Render-ისთვის საჭირო პორტი
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
