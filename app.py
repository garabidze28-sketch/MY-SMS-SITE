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

        /* გულების ანიმაცია */
        .heart { position: fixed; color: #ff4d4d; font-size: 20px; animation: float 6s infinite linear; opacity: 0; pointer-events: none; z-index: 0; }
        @keyframes float {
            0% { transform: translateY(100vh) scale(0.5); opacity: 0; }
            50% { opacity: 0.8; }
            100% { transform: translateY(-10vh) scale(1.2); opacity: 0; }
        }

        .card { background: white; border-radius: 20px; padding: 25px; box-shadow: 0 10px 30px rgba(0,0,0,0.05); margin-bottom: 20px; border: 1px solid #f1f5f9; text-align: center; }
        
        label { display: block; text-align: left; margin-bottom: 8px; font-weight: 600; font-size: 14px; color: #374151; }
        input[type="text"], textarea, input[type="file"] { width: 100%; padding: 14px; border: 1px solid #e2e8f0; border-radius: 12px; box-sizing: border-box; font-size: 16px; margin-bottom: 15px; outline: none; transition: 0.2s; }
        input:focus { border-color: var(--main-red); box-shadow: 0 0 0 3px rgba(225, 29, 72, 0.1); }

        /* BOG სექცია */
        .bank-card { background: #fff; border: 2px solid #f1f5f9; border-radius: 15px; padding: 15px; display: flex; align-items: center; gap: 12px; cursor: pointer; transition: 0.2s; }
        .bank-card:hover { border-color: #f97316; background: #fffaf5; }
        .bank-logo { width: 45px; height: 45px; border-radius: 10px; background: #f97316; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; font-size: 10px; line-height: 1; text-align: center; }
        .iban { font-family: 'Courier New', monospace; font-weight: bold; color: #1e293b; font-size: 14px; word-break: break-all; }

        .btn-send { width: 100%; background: var(--main-red); color: white; border: none; padding: 18px; border-radius: 14px; font-size: 18px; font-weight: bold; cursor: pointer; box-shadow: 0 4px 15px rgba(225, 29, 72, 0.3); transition: 0.3s; }
        .btn-send:active { transform: scale(0.97); }

        .footer-note { background: #f8fafc; padding: 15px; border-radius: 12px; font-size: 13px; color: #64748b; text-align: left; border-left: 4px solid var(--main-red); margin-top: 10px; }
    </style>
</head>
<body>

<header>
    <div style="letter-spacing: 1px;">GeoSMS</div>
    <div style="cursor:pointer; font-size: 28px;" onclick="toggleMenu()">☰</div>
</header>

<div class="sidebar" id="sidebar">
    <div style="text-align: right; cursor: pointer; font-size: 24px;" onclick="toggleMenu()">✕</div>
    <h3>მენიუ</h3>
    <a href="/">მთავარი</a>
    <a href="#" onclick="alert('კონტაქტი:\\nEmail: support@geosms.ge\\nTelegram: @GeoSMS_Support')">კონტაქტი</a>
    <a href="#" onclick="alert('წესები:\\n1. ანონიმურობა დაცულია\\n2. მუქარა აკრძალულია\\n3. ჩეკი მოწმდება ადმინისტრაციის მიერ')">წესები</a>
    <p style="font-size: 11px; color: #4b5563; margin-top: 60px;">© 2026 GeoSMS.ge</p>
</div>

<div class="container" id="heart-container">
    <div class="card">
        <h2 style="margin: 0; color: var(--main-red);">ანონიმური SMS</h2>
        <p style="color: #64748b; font-size: 15px; margin-top: 5px;">გააგზავნე მესიჯი 2 ლარად</p>
    </div>

    <form action="/submit" method="POST" enctype="multipart/form-data" class="card">
        <label>მიმღების ნომერი</label>
        <input type="text" name="phone" placeholder="მაგ: 571XXXXXX" required>
        
        <label>შეტყობინება (English Only)</label>
        <textarea name="message" rows="3" placeholder="გამარჯობა..." required></textarea>

        <label>გადახდა (BOG)</label>
        <div class="bank-card" onclick="copyIban()">
            <div class="bank-logo">BANK OF<br>GEO</div>
            <div style="text-align: left;">
                <div class="iban">GE38BG0000000581620953</div>
                <div style="font-size: 11px; color: #f97316; font-weight: bold;">მიმღები: გ.ა (დააჭირე კოპირებისთვის)</div>
            </div>
        </div>

        <label style="margin-top: 20px;">ატვირთე გადახდის ჩეკი</label>
        <input type="file" name="receipt" accept="image/*" required>

        <div style="display: flex; align-items: center; gap: 10px; margin: 15px 0; text-align: left;">
            <input type="checkbox" id="agree" style="width: 20px; height: 20px;" required>
            <label for="agree" style="margin: 0; font-weight: normal;">ვეთანხმები წესებს</label>
        </div>

        <button type="submit" class="btn-send">გაგზავნა</button>
    </form>

    <div class="footer-note">
        <b>ინფორმაცია:</b><br>
        ჩეკის ატვირთვის შემდეგ, ადმინისტრაცია გადაამოწმებს გადარიცხვას და მესიჯი გაიგზავნება მომენტალურად.
    </div>
</div>

<script>
    function toggleMenu() { document.getElementById('sidebar').classList.toggle('active'); }
    function copyIban() {
        navigator.clipboard.writeText("GE38BG0000000581620953");
        alert("IBAN კოდი დაკოპირდა!");
    }
    function createHeart() {
        const container = document.getElementById('heart-container');
        const heart = document.createElement('div');
        heart.innerHTML = '❤️';
        heart.className = 'heart';
        heart.style.left = Math.random() * 100 + 'vw';
        heart.style.animationDuration = (Math.random() * 2 + 4) + 's';
        document.body.appendChild(heart);
        setTimeout(() => heart.remove(), 6000);
    }
    setInterval(createHeart, 700);
</script>

</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/submit', methods=['POST'])
def submit():
    phone = request.form.get('phone').replace(" ", "")
    msg = request.form.get('message')
    receipt = request.files.get('receipt')

    # ნომრის ავტომატური გასწორება +995-ზე
    if not phone.startswith('+'):
        if phone.startswith('0'): phone = phone[1:]
        phone = '+995' + phone

    # 1. ფოტოს და მონაცემების გაგზავნა შენს Telegram ბოტში
    if TG_TOKEN and TG_CHAT_ID:
        try:
            tg_url = f"https://api.telegram.org/bot{TG_TOKEN}/sendPhoto"
            # ვკითხულობთ ფაილს გასაგზავნად
            receipt_data = receipt.read()
            files = {'photo': ('receipt.jpg', receipt_data)}
            caption = f"🔔 ახალი SMS შეკვეთა!\\n\\n📱 ნომერი: {phone}\\n💬 მესიჯი: {msg}"
            requests.post(tg_url, data={'chat_id': TG_CHAT_ID, 'caption': caption}, files=files)
        except Exception as e:
            print(f"Telegram error: {e}")

    # 2. SMS-ის გაგზავნა Twilio-თი
    status_msg = ""
    success = False
    if client:
        try:
            client.messages.create(body=f"GeoSMS: {msg}", from_=TWILIO_NUMBER, to=phone)
            status_msg = "მესიჯი წარმატებით გაიგზავნა!"
            success = True
        except Exception as e:
            status_msg = f"შეცდომა: {str(e)}"
    else:
        status_msg = "Twilio კონფიგურაციის შეცდომა"

    return f'''
    <div style="font-family: sans-serif; text-align: center; padding: 50px; background: #f9fafb; min-height: 100vh;">
        <div style="background: white; border: 2px solid {'#10b981' if success else '#ef4444'}; display: inline-block; padding: 40px; border-radius: 24px; box-shadow: 0 20px 40px rgba(0,0,0,0.05);">
            <h1 style="color: {'#10b981' if success else '#ef4444'}; font-size: 40px; margin-bottom: 10px;">{'✅' if success else '❌'}</h1>
            <h2 style="color: #1e293b; margin-bottom: 20px;">{status_msg}</h2>
            <p style="color: #64748b; margin-bottom: 30px;">ჩეკი მიღებულია და გადამოწმდება ადმინისტრაციის მიერ.</p>
            <a href="/" style="text-decoration: none; color: white; background: #e11d48; padding: 15px 30px; border-radius: 12px; font-weight: bold; transition: 0.3s;">მთავარზე დაბრუნება</a>
        </div>
    </div>
    '''

if __name__ == '__main__':
    app.run(debug=True)
