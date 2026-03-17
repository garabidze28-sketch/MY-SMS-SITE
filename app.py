import os
from flask import Flask, render_template_string, request, jsonify
from supabase import create_client, Client

app = Flask(__name__)

# --- მონაცემები ---
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    print(f"Error connecting to Supabase: {e}")

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ka">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>მხარდაჭერა</title>
    <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.5.1/dist/confetti.browser.min.js"></script>
    <style>
        :root { --gold: #f6e05e; --orange: #ed8936; --dark: #0a0a0a; }
        body { font-family: 'Segoe UI', sans-serif; background: var(--dark); color: white; margin: 0; text-align: center; scroll-behavior: smooth; overflow-x: hidden; }
        
        /* ლოგინი */
        #login-overlay { position: fixed; inset: 0; background: var(--dark); z-index: 2000; display: flex; align-items: center; justify-content: center; transition: 0.5s; }
        .login-card { background: #111; padding: 40px; border-radius: 30px; border: 1px solid var(--gold); width: 85%; max-width: 380px; box-shadow: 0 0 30px rgba(246, 224, 94, 0.2); }
        
        /* ნავიგაცია */
        nav { background: rgba(0,0,0,0.9); padding: 15px; display: flex; justify-content: center; gap: 20px; position: sticky; top: 0; z-index: 100; border-bottom: 1px solid #222; backdrop-filter: blur(10px); }
        nav a { color: white; text-decoration: none; font-weight: bold; font-size: 14px; cursor: pointer; transition: 0.3s; opacity: 0.8; }
        nav a:hover { opacity: 1; color: var(--gold); }
        
        .container { max-width: 500px; margin: 20px auto; padding: 0 15px; }
        .card { background: #111; padding: 25px; border-radius: 25px; border: 1px solid #222; margin-bottom: 20px; position: relative; }
        
        .progress-bg { background: #222; height: 25px; border-radius: 15px; overflow: hidden; margin: 15px 0; border: 1px solid #333; }
        .progress-fill { background: linear-gradient(90deg, var(--gold), var(--orange)); height: 100%; width: 0%; transition: 2s cubic-bezier(0.1, 0, 0.1, 1); }
        
        .btn { background: var(--gold); color: black; border: none; padding: 16px; border-radius: 50px; font-size: 16px; font-weight: bold; cursor: pointer; transition: 0.3s; margin: 10px 0; width: 100%; display: flex; align-items: center; justify-content: center; gap: 10px; }
        .btn:active { transform: scale(0.98); }
        .btn:disabled { background: #333; color: #777; cursor: not-allowed; }
        
        .google-btn { background: white; color: #444; margin-top: 15px; }
        .input-style { background: #1a1a1a; border: 1px solid #333; padding: 15px; border-radius: 15px; color: white; width: 100%; margin-bottom: 15px; box-sizing: border-box; text-align: center; font-size: 16px; }
        
        /* Countdown & Timer */
        #timer { font-family: monospace; font-size: 22px; color: var(--gold); margin-top: 10px; font-weight: bold; }
        
        /* IBAN Styling */
        .iban-container { background: rgba(246, 224, 94, 0.05); border: 2px dashed #444; padding: 20px; border-radius: 20px; cursor: pointer; transition: 0.3s; }
        .iban-container:hover { border-color: var(--gold); }
        
        /* Custom Notifications */
        .toast { position: fixed; bottom: -100px; left: 50%; transform: translateX(-50%); background: var(--gold); color: black; padding: 15px 30px; border-radius: 50px; font-weight: bold; transition: 0.5s; z-index: 3000; box-shadow: 0 10px 20px rgba(0,0,0,0.5); }
        .toast.show { bottom: 30px; }
        
        .music-control { position: fixed; bottom: 20px; left: 20px; background: rgba(0,0,0,0.8); width: 50px; height: 50px; border-radius: 50%; border: 1px solid var(--gold); cursor: pointer; z-index: 1000; display: flex; align-items: center; justify-content: center; font-size: 20px; }
    </style>
</head>
<body>

    <div id="login-overlay">
        <div class="login-card">
            <h2 style="color:var(--gold); margin-top:0;">ავტორიზაცია</h2>
            <p style="font-size: 14px; opacity: 0.7;">გაიარეთ რეგისტრაცია გასაგრძელებლად</p>
            <input type="number" id="user-phone" class="input-style" placeholder="ტელეფონის ნომერი...">
            <button class="btn" onclick="saveUser()">შესვლა ნომრით</button>
            <div style="margin: 15px 0; opacity: 0.3;">⎯⎯⎯⎯  ან  ⎯⎯⎯⎯</div>
            <button class="btn google-btn" onclick="googleLogin()">
                <img src="https://www.gstatic.com/images/branding/product/1x/gsa_512dp.png" width="20"> Google-ით შესვლა
            </button>
        </div>
    </div>

    <nav>
        <a onclick="location.reload()">მთავარი</a>
        <a href="#rules">წესები</a>
        <a href="#top">TOP 10</a>
    </nav>

    <div class="music-control" onclick="toggleMusic()" id="music-btn">🔇</div>
    <div id="toast-notif" class="toast">✅ ანგარიშის ნომერი დაკოპირდა!</div>

    <div class="container">
        <h2 id="welcome-msg" style="color: var(--gold); font-size: 18px;">მხარდაჭერის პლატფორმა</h2>

        <div class="card">
            <h3 style="margin:0; opacity: 0.8;">საერთო მიზანი</h3>
            <h1 style="margin:10px 0; color:var(--gold);">10,000₾</h1>
            <div class="progress-bg"><div class="progress-fill" id="bar"></div></div>
            <p>სულ შეგროვდა: <span class="gold-text" id="total-val">0</span>₾</p>
        </div>

        <div class="card">
            <h2 style="font-size: 22px; margin-top:0;">✨ იღბლის წინასწარმეტყველება</h2>
            <div id="fortune-text" style="min-height: 50px; font-size: 17px; margin: 15px 0; color: #ddd;">გაიგე რა გელის დღეს...</div>
            <button id="fortune-btn" class="btn" onclick="getFortune()">გამოცადე იღბალი</button>
            <div id="timer-box" style="display:none;">
                <p style="font-size:12px; margin-bottom:5px; opacity:0.6;">შემდეგი იღბალი ხელმისაწვდომია:</p>
                <div id="timer">00:00:00</div>
            </div>
        </div>

        <div class="card" id="rules">
            <h3 style="color:var(--gold); margin-top:0;">📜 საიტის წესები</h3>
            <div style="text-align: left; font-size: 14px; opacity: 0.8; line-height: 1.7;">
                1. მხარდაჭერა არის ნებაყოფლობითი.<br>
                2. იღბლის გამოცდა ხდება 24 საათში ერთხელ.<br>
                3. მონაცემები ახლდება ყოველ 5 წამში.<br>
                4. ნებისმიერი მხარდაჭერა მნიშვნელოვანია!
            </div>
        </div>

        <div class="card">
            <p style="margin-bottom: 15px;">მხარდასაჭერი IBAN (BOG):</p>
            <div class="iban-container" onclick="copyIBAN()">
                <strong style="color:var(--gold); font-size:16px; letter-spacing: 1px;">GE38BG0000000581620953</strong>
                <p style="font-size:11px; margin-top:8px; opacity:0.6;">მიმღები: გ.ა | დანიშნულება: მხარდაჭერა</p>
            </div>
        </div>

        <div class="card" id="top">
            <h3 style="color:var(--gold); margin-top:0;">🏆 TOP 10 მხარდამჭერი</h3>
            <div id="leaderboard" style="font-size: 15px;">იტვირთება...</div>
        </div>
    </div>

    <audio id="bgMusic" loop preload="auto">
        <source src="https://www.soundhelix.com/examples/mp3/SoundHelix-Song-8.mp3" type="audio/mpeg">
    </audio>

    <script>
        let lastCount = 0;

        // ლოგინის ლოგიკა
        function saveUser() {
            const phone = document.getElementById('user-phone').value;
            if(phone.length >= 9) {
                localStorage.setItem('user_auth', phone);
                document.getElementById('login-overlay').style.opacity = '0';
                setTimeout(() => document.getElementById('login-overlay').remove(), 500);
            } else { alert("შეიყვანეთ სწორი ნომერი"); }
        }

        function googleLogin() {
            // აქ რეალური Google Auth-ისთვის Supabase-ის კონფიგურაციაა საჭირო
            localStorage.setItem('user_auth', 'google_user');
            location.reload();
        }

        window.onload = function() {
            if(localStorage.getItem('user_auth')) {
                document.getElementById('login-overlay').remove();
            }
            updateTimer();
            loadData();
            setInterval(updateTimer, 1000);
        };

        // 24 საათიანი Countdown
        function updateTimer() {
            const lastTime = localStorage.getItem('lastFortuneTime');
            if (!lastTime) return;

            const nextTime = parseInt(lastTime) + (24 * 60 * 60 * 1000);
            const now = new Date().getTime();
            const diff = nextTime - now;

            if (diff > 0) {
                document.getElementById('fortune-btn').style.display = 'none';
                document.getElementById('timer-box').style.display = 'block';
                
                const h = Math.floor(diff / (1000 * 60 * 60));
                const m = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
                const s = Math.floor((diff % (1000 * 60)) / 1000);
                
                document.getElementById('timer').innerText = 
                    `${h.toString().padStart(2,'0')}:${m.toString().padStart(2,'0')}:${s.toString().padStart(2,'0')}`;
            } else {
                document.getElementById('fortune-btn').style.display = 'flex';
                document.getElementById('timer-box').style.display = 'none';
            }
        }

        async function loadData() {
            try {
                const resp = await fetch('/api/data');
                const data = await resp.json();
                document.getElementById('bar').style.width = Math.min((data.total / 10000) * 100, 100) + '%';
                document.getElementById('total-val').innerText = data.total;
                let html = '';
                data.top.forEach((item, index) => {
                    html += `<div style="display:flex; justify-content:space-between; padding:10px; border-bottom:1px solid #222;">
                                <span>${index+1}. ${item.name}</span><span style="color:var(--gold)">${item.amount}₾</span>
                             </div>`;
                });
                document.getElementById('leaderboard').innerHTML = html || "მონაცემები არ არის";
            } catch (e) {}
        }

        function getFortune() {
            const f = ["დღეს დიდი იღბალი გელის!", "ვიღაც შენზე კარგს ფიქრობს", "საუკეთესო დღეა ახალი საქმისთვის", "სურვილი აგისრულდება!", "მოულოდნელი საჩუქარი გელის"];
            document.getElementById('fortune-text').innerText = f[Math.floor(Math.random()*f.length)];
            confetti({ particleCount: 150, spread: 70 });
            localStorage.setItem('lastFortuneTime', new Date().getTime());
            updateTimer();
        }

        function copyIBAN() {
            navigator.clipboard.writeText('GE38BG0000000581620953');
            const toast = document.getElementById('toast-notif');
            toast.classList.add('show');
            setTimeout(() => toast.classList.remove('show'), 3000);
        }

        function toggleMusic() {
            const m = document.getElementById('bgMusic');
            const btn = document.getElementById('music-btn');
            if (m.paused) { m.play().catch(e=>alert("დააჭირეთ ეკრანს მუსიკისთვის")); btn.innerText = "🔊"; } 
            else { m.pause(); btn.innerText = "🔇"; }
        }

        setInterval(loadData, 5000);
    </script>
</body>
</html>
'''

@app.route('/')
def index(): return render_template_string(HTML_TEMPLATE)

@app.route('/api/data')
def get_data():
    try:
        res = supabase.table('donations').select('*').execute()
        total = sum(item['amount'] for item in res.data)
        top = sorted(res.data, key=lambda x: x['amount'], reverse=True)[:10]
        return jsonify({'total': total, 'top': top, 'count': len(res.data)})
    except: return jsonify({'total': 0, 'top': [], 'count': 0})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
