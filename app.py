import os
import requests
from flask import Flask, render_template_string, request

app = Flask(__name__)

# ტელეგრამის მონაცემები
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

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
        
        /* Navbar */
        header { background: var(--main-red); padding: 15px 20px; display: flex; justify-content: space-between; align-items: center; color: white; position: sticky; top: 0; z-index: 1000; }
        .logo { font-size: 24px; font-weight: bold; letter-spacing: 1px; }

        /* Container */
        .container { max-width: 480px; margin: 0 auto; padding: 20px; position: relative; }

        /* Hearts */
        .heart { position: absolute; color: #ff4d4d; font-size: 18px; user-select: none; z-index: 1; animation: float 4s infinite ease-in-out; opacity: 0.8; }
        @keyframes float { 0% { transform: translateY(0); opacity: 0.8; } 50% { transform: translateY(-20px); opacity: 1; } 100% { transform: translateY(0); opacity: 0.8; } }

        /* Form Styling */
        .card { border: 1px solid #eee; border-radius: 10px; padding: 20px; background: white; margin-bottom: 20px; }
        h2 { font-size: 22px; text-align: center; margin-bottom: 20px; }
        
        label { display: block; margin-bottom: 8px; font-weight: bold; font-size: 14px; color: #333; }
        input[type="text"], textarea, input[type="file"], select { 
            width: 100%; padding: 12px; margin-bottom: 20px; border: 1px solid #ccc; border-radius: 8px; box-sizing: border-box; font-size: 16px; 
        }

        /* Bank Section */
        .bank-card { border: 1px solid #333; border-radius: 12px; padding: 12px; display: flex; align-items: center; gap: 12px; cursor: pointer; margin-top: 10px; }
        .bank-logo { width: 40px; height: 40px; }
        .iban-text { font-family: monospace; font-size: 14px; font-weight: bold; }

        /* Checkbox სექცია - ზუსტად SMISSY-ს სტილში */
        .terms-container { display: flex; align-items: center; gap: 10px; margin-bottom: 20px; font-size: 14px; color: #555; }
        .terms-container input[type="checkbox"] { width: 18px; height: 18px; margin: 0; cursor: pointer; }
        .terms-container a { color: #007bff; text-decoration: none; }

        /* გაგზავნის ღილაკი */
        .btn-send { width: 100%; background: #fff; border: 1px solid #ccc; padding: 14px; border-radius: 8px; font-size: 16px; cursor: pointer; font-weight: bold; transition: 0.2s; }
        .btn-send:hover { background: #f9f9f9; }

        /* Rules */
        .rule-card { border: 1px solid #eee; border-radius: 8px; padding: 15px; margin-bottom: 10px; }
        .rule-card h4 { margin: 0 0 5px 0; }
    </style>
</head>
<body>

<header>
    <div class="logo">SMISSY</div>
    <div style="font-size: 24px;">☰</div>
</header>

<div class="container">
    <div class="heart" style="top: 10%; left: 5%;">❤️</div>
    <div class="heart" style="top: 30%; right: 10%;">❤️</div>

    <div class="card" style="text-align: center;">
        <h3 style="margin: 0;">ანონიმური მესიჯები 2 ლარად</h3>
        <p style="font-size: 14px; color: #666;">გთავაზობთ ანონიმური მესიჯების გაგზავნის შესაძლებლობას ნებისმიერ ნომერზე!</p>
    </div>

    <form action="/submit-order" method="POST" enctype="multipart/form-data">
        <label>ნომერი</label>
        <input type="text" name="phone" placeholder="მაგ: 599XXXXXX" required>
        
        <label>სახელი</label>
        <input type="text" name="sender_name" placeholder="სახელი">

        <label>მესიჯი</label>
        <textarea name="message" rows="4" placeholder="მესიჯი უნდა შეიცავდეს მხოლოდ ინგლისურ ასოებს" required></textarea>

        <label>აირჩიეთ ბანკი</label>
        <select>
            <option>Bank of Georgia (საქართველოს ბანკი)</option>
        </select>

        <div class="bank-card" onclick="copyIban()">
            <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/1/15/Bank_of_Georgia_logo.svg/1024px-Bank_of_Georgia_logo.svg.png" class="bank-logo">
            <div>
                <div class="iban-text">GE38BG0000000581620953</div>
                <div style="font-size: 12px; color: #666;">მიმღები: გ.ა</div>
            </div>
        </div>
        <p style="font-size: 11px; text-align: center; color: #999; margin-bottom: 20px;">(დააჭირე დასაკოპირებლად)</p>

        <label>გადახდის ქვითარი</label>
        <input type="file" name="receipt" accept="image/*" required>

        <div class="terms-container">
            <input type="checkbox" id="terms" required>
            <label for="terms" style="display: inline; font-weight: normal;">ვეთანხმები <a href="#">წესებსა და პირობებს</a></label>
        </div>

        <button type="submit" class="btn-send">გაგზავნა</button>
    </form>

    <h2 style="margin-top: 40px;">წესები</h2>
    <div class="rule-card">
        <h4>1. ანონიმური გაგზავნა</h4>
        <p style="font-size: 13px; color: #666;">თქვენი ვინაობა არავისთვის იქნება ცნობილი.</p>
    </div>
    <div class="rule-card">
        <h4>2. მუქარა</h4>
        <p style="font-size: 13px; color: #666;">მუქარის შემთხვევაში ინფორმაცია გადაეცემა პოლიციას.</p>
    </div>
</div>

<script>
    function copyIban() {
        navigator.clipboard.writeText("GE38BG0000000581620953");
        alert("ანგარიშის ნომერი დაკოპირდა!");
    }
</script>

</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/submit-order', methods=['POST'])
def submit_order():
    phone = request.form.get('phone')
    name = request.form.get('sender_name', 'ანონიმი')
    msg = request.form.get('message')
    receipt = request.files.get('receipt')

    caption = f"🔔 ახალი შეკვეთა!\\n\\n📱 ნომერი: {phone}\\n👤 სახელი: {name}\\n💬 მესიჯი: {msg}"
    
    # გაგზავნა ტელეგრამზე
    requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", 
                  data={"chat_id": CHAT_ID, "text": caption})
    
    if receipt:
        files = {'photo': receipt.read()}
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto", 
                      params={'chat_id': CHAT_ID}, files=files)

    return "<h2>შეკვეთა გაიგზავნა! ადმინი მალე შეამოწმებს.</h2><a href='/'>უკან</a>"

if __name__ == '__main__':
    app.run(debug=True)
