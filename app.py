import os
from flask import Flask, render_template_string, request
from twilio.rest import Client

app = Flask(__name__)

# Twilio მონაცემები
TWILIO_SID = os.environ.get('TWILIO_SID')
TWILIO_TOKEN = os.environ.get('TWILIO_TOKEN')
TWILIO_NUMBER = os.environ.get('TWILIO_NUMBER')

client = Client(TWILIO_SID, TWILIO_TOKEN) if TWILIO_SID and TWILIO_TOKEN else None

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ka">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GeoSMS - ანონიმური მესიჯები</title>
    <style>
        :root { --main-red: #e11d48; }
        body { font-family: 'Helvetica Neue', Arial, sans-serif; background: #fdfdfd; margin: 0; overflow-x: hidden; }
        
        /* ჰედერი */
        header { background: var(--main-red); padding: 15px; color: white; display: flex; justify-content: space-between; align-items: center; font-weight: bold; font-size: 22px; position: sticky; top: 0; z-index: 100; }
        
        .container { max-width: 450px; margin: 0 auto; padding: 20px; position: relative; }

        /* მფრინავი გულები */
        .heart { position: absolute; color: #ff4d4d; font-size: 20px; animation: float 5s infinite linear; opacity: 0; z-index: 0; }
        @keyframes float {
            0% { transform: translateY(100vh) rotate(0deg); opacity: 1; }
            100% { transform: translateY(-10vh) rotate(360deg); opacity: 0; }
        }

        .card { background: white; border-radius: 15px; padding: 20px; box-shadow: 0 5px 15px rgba(0,0,0,0.08); margin-bottom: 20px; text-align: center; position: relative; z-index: 1; }
        
        label { display: block; text-align: left; margin: 10px 0 5px; font-weight: bold; font-size: 14px; }
        input, textarea { width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 10px; box-sizing: border-box; font-size: 16px; margin-bottom: 15px; }

        /* ბანკის სექცია */
        .bank-card { border: 2px solid #eee; border-radius: 12px; padding: 12px; display: flex; align-items: center; gap: 12px; background: #fafafa; cursor: pointer; }
        .bank-logo { width: 45px; height: 45px; object-fit: contain; }
        .iban { font-family: monospace; font-weight: bold; font-size: 13px; color: #333; }

        .btn-send { width: 100%; background: var(--main-red); color: white; border: none; padding: 16px; border-radius: 10px; font-size: 18px; font-weight: bold; cursor: pointer; transition: 0.3s; margin-top: 10px; }
        .btn-send:hover { background: #be123c; }

        .footer-info { font-size: 12px; color: #777; margin-top: 20px; line-height: 1.6; text-align: left; background: #eee; padding: 10px; border-radius: 8px; }
    </style>
</head>
<body>

<header>
    <div>GeoSMS</div>
    <div onclick="alert('მენიუ მალე დაემატება')">☰</div>
</header>

<div class="container" id="heart-container">
    <div class="card">
        <h2 style="margin: 0; color: var(--main-red);">GeoSMS</h2>
        <p style="color: #666; font-size: 14px;">გააგზავნე ანონიმური SMS 2 ლარად</p>
    </div>

    <form action="/submit" method="POST" enctype="multipart/form-data" class="card">
        <label>მიმღების ნომერი</label>
        <input type="text" name="phone" placeholder="+995 599 XX XX XX" required>
        
        <label>შეტყობინება (English Only)</label>
        <textarea name="message" rows="3" placeholder="დაწერე მესიჯი..." required></textarea>

        <label>გადახდა (BOG)</label>
        <div class="bank-card" onclick="copyIban()">
            <img src="https://upload.wikimedia.org/wikipedia/commons/1/15/Bank_of_Georgia_logo.svg" class="bank-logo">
            <div style="text-align: left;">
                <div class="iban">GE38BG0000000581620953</div>
                <div style="font-size: 11px; color: #666;">მიმღები: გ.ა</div>
            </div>
        </div>

        <label style="margin-top:15px;">ატვირთე ჩეკის ფოტო</label>
        <input type="file" name="receipt" accept="image/*" required>

        <div style="display: flex; align-items: center; gap: 8px; margin: 10px 0;">
            <input type="checkbox" style="width: 18px; margin: 0;" required>
            <span style="font-size: 13px;">ვეთანხმები წესებს</span>
        </div>

        <button type="submit" class="btn-send">გაგზავნა</button>
    </form>

    <div class="footer-info">
        <b>წესები:</b><br>
        1. მესიჯი იგზავნება ანონიმურად.<br>
        2. იკრძალება მუქარა და შეურაცხყოფა.<br>
        3. არასწორი ნომრის შემთხვევაში თანხა არ ბრუნდება.
    </div>
</div>

<script>
    function copyIban() {
        navigator.clipboard.writeText("GE38BG0000000581620953");
        alert("IBAN დაკოპირდა!");
    }

    // გულების გენერატორი
    function createHeart() {
        const container = document.getElementById('heart-container');
        const heart = document.createElement('div');
        heart.innerHTML = '❤️';
        heart.className = 'heart';
        heart.style.left = Math.random() * 100 + '%';
        heart.style.animationDuration = (Math.random() * 3 + 2) + 's';
        container.appendChild(heart);
        setTimeout(() => heart.remove(), 5000);
    }
    setInterval(createHeart, 800);
</script>

</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/submit', methods=['POST'])
def submit():
    phone = request.form.get('phone')
    msg = request.form.get('message')
    
    # აქ ხდება SMS-ის გაგზავნა
    status_msg = ""
    if client:
        try:
            client.messages.create(body=msg, from_=TWILIO_NUMBER, to=phone)
            status_msg = "✅ მესიჯი გაიგზავნა წარმატებით!"
        except Exception as e:
            status_msg = f"❌ შეცდომა: {str(e)}"
    else:
        status_msg = "⚠️ Twilio კონფიგურაცია აკლია!"

    return f"""
    <div style="font-family: sans-serif; text-align: center; padding: 50px;">
        <div style="border: 2px solid #e11d48; display: inline-block; padding: 20px; border-radius: 15px;">
            <h2 style="color: #e11d48;">{status_msg}</h2>
            <p>ჩეკი მიღებულია. მადლობა GeoSMS-ის გამოყენებისთვის!</p>
            <a href="/" style="text-decoration: none; color: white; background: #e11d48; padding: 10px 20px; border-radius: 8px;">უკან დაბრუნება</a>
        </div>
    </div>
    """

if __name__ == '__main__':
    app.run(debug=True)
