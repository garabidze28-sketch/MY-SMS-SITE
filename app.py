import os
from flask import Flask, render_template_string, request, jsonify
from supabase import create_client, Client

app = Flask(__name__)

# --- Supabase Setup ---
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    print(f"Supabase Error: {e}")

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ka">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NEXUS - მხარდაჭერა</title>
    <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.5.1/dist/confetti.browser.min.js"></script>
    <style>
        :root { --gold: #f6e05e; --orange: #ed8936; --dark: #0a0a0a; --card: #141414; }
        body { font-family: 'Segoe UI', system-ui, sans-serif; background: var(--dark); color: white; margin: 0; text-align: center; scroll-behavior: smooth; overflow-x: hidden; }
        
        /* Login Overlay */
        #login-overlay { position: fixed; inset: 0; background: var(--dark); z-index: 9999; display: flex; align-items: center; justify-content: center; }
        .login-card { background: var(--card); padding: 40px; border-radius: 30px; border: 1px solid var(--gold); width: 85%; max-width: 380px; box-shadow: 0 0 50px rgba(246, 224, 94, 0.1); }
        
        /* Navigation */
        nav { background: rgba(0,0,0,0.9); padding: 15px; display: flex; justify-content: center; gap: 25px; position: sticky; top: 0; z-index: 100; border-bottom: 1px solid #222; backdrop-filter: blur(10px); }
        nav a { color: white; text-decoration: none; font-weight: bold; font-size: 14px; cursor: pointer; transition: 0.3s; opacity: 0.8; }
        nav a:hover { opacity: 1; color: var(--gold); }
        
        .container { max-width: 500px; margin: 20px auto; padding: 0 15px; display: none; }
        .card { background: var(--card); padding: 25px; border-radius: 25px; border: 1px solid #222; margin-bottom: 20px; position: relative; border-bottom: 3px solid #222; }
        
        .progress-bg { background: #000; height: 18px; border-radius: 20px; overflow: hidden; margin: 20px 0; border: 1px solid #333; }
        .progress-fill { background: linear-gradient(90deg, var(--gold), var(--orange)); height: 100%; width: 0%; transition: 2s cubic-bezier(0.1, 0, 0.1, 1); }
        
        .btn { background: var(--gold); color: black; border: none; padding: 16px; border-radius: 50px; font-size: 16px; font-weight: bold; cursor: pointer; transition: 0.3s; width: 100%; margin: 10px 0; }
        .btn:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(246, 224, 94, 0.2); }
        
        .google-btn { background: white; color: #333; display: flex; align-items: center; justify-content: center; gap: 10px; }
        .input-style { background: #000; border: 1px solid #333; padding: 15px; border-radius: 15px; color: white; width: 100%; margin-bottom: 15px; box-sizing: border-box; text-align: center; font-size: 16px; outline: none; }
        .input-style:focus { border-color: var(--gold); }

        /* Toast Message */
        #toast { position: fixed; bottom: -100px; left: 50%; transform: translateX(-50%); background: var(--gold); color: black; padding: 15px 30px; border-radius: 50px; font-weight: bold; transition: 0.5s; z-index: 10000; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
        #toast.show { bottom: 30px; }

        .music-control { position: fixed; bottom: 20px; left: 20px; background: rgba(0,0,0,0.8); width: 50px; height: 50px; border-radius: 50%; border: 1px solid var(--gold); cursor: pointer; z-index: 1000; display: flex; align-items: center; justify-content: center; font-size: 20px; }
        
        .leader-item { display: flex; justify-content: space-between; padding: 12px; border-bottom: 1px solid #222; }
        #timer { font-size: 24px; color: var(--gold); font-weight: bold; font-family: monospace; }
    </style>
</head>
<body>

    <div id="toast">✅ IBAN დაკოპირდა!</div>

    <div id="login-overlay">
        <div class="login-card">
            <h2 style="color:var(--gold); margin-top:0;">NEXUS CLUB</h2>
            <p style="opacity:0.7; font-size: 14px;">შეიყვანეთ სახელი ან ნომერი</p>
            <input type="text" id="user-input" class="input-style" placeholder="სახელი / ტელეფონი...">
            <button class="btn" onclick="loginAction()">შესვლა</button>
            <div style="margin:10px; opacity:0.3; font-size: 12px;">⎯⎯⎯⎯  ან  ⎯⎯⎯⎯</div>
            <button class="btn google-btn" onclick="loginAction('Google User')">
                <img src="https://www.gstatic.com/images/branding/product/1x/gsa_512dp.png" width="18"> Google შესვლა
            </button>
        </div>
    </div>

    <nav>
        <a onclick="window.scrollTo({top:0, behavior:'smooth'})">მთავარი</a>
        <a href="#rules-box">წესები</a>
        <a href="#top-box">TOP 10</a>
    </nav>

    <div class="music-control" onclick="toggleMusic()" id="music-btn">🔇</div>

    <div class="container" id="main-content">
        <h3 id="user-greet" style="color: var(--gold); font-size: 16px; margin-bottom: 25px;">გამარჯობა!</h3>

        <div class="card">
            <p style="margin:0; opacity: 0.6; font-size: 14px;">საერთო მიზანი</p>
            <h1 style="margin:10px 0; font-size: 42px; color: var(--gold);">10,000₾</h1>
            <div class="progress-bg"><div class="progress-fill" id="bar"></div></div>
            <p style="font-size: 18px;">შეგროვდა: <span id="total-val" style="color:var(--gold); font-weight:bold;">0</span>₾</p>
        </div>

        <div class="card">
            <h3 style="margin-top:0;">✨ იღბლის წინასწარმეტყველება</h3>
            <div id="fortune-text" style="min-height: 60px; display:flex; align-items:center; justify-content:center; color: #ddd; font-size: 18px;">დააჭირე ღილაკს...</div>
            <button id="fortune-btn" class="btn" onclick="getFortune()">გამოცადე იღბალი</button>
            <div id="timer-box" style="display:none; margin-top:10px;">
                <p style="font-size:12px; opacity:0.5; margin-bottom:5px;">შემდეგი მცდელობა:</p>
                <div id="timer">00:00:00</div>
            </div>
        </div>

        <div class="card" id="rules-box">
            <h3 style="color:var(--gold); margin-top:0;">📜 საიტის წესები</h3>
            <div style="text-align: left; font-size: 14px; opacity: 0.8; line-height: 1.8;">
                • მხარდაჭერა არის ნებაყოფლობითი.<br>
                • იღბლის ნახვა შეგიძლიათ 24 საათში ერთხელ.<br>
                • მონაცემები ახლდება ავტომატურად ყოველ 5 წამში.<br>
                • ნებისმიერი თანხა ეხმარება NEXUS-ის განვითარებას.
            </div>
        </div>

        <div class="card">
            <p style="margin-bottom:15px; font-size:14px;">მხარდასაჭერი IBAN (BOG):</p>
            <div style="background:#080808; border:2px dashed #333; padding:20px; border-radius:20px; cursor:pointer; transition:0.3s;" onclick="copyIBAN()" onmouseover="this.style.borderColor='#f6e05e'" onmouseout="this.style.borderColor='#333'">
                <strong style="color:var(--gold); letter-spacing:1px; font-family:monospace; font-size:17px;">GE38BG0000000581620953</strong>
                <p style="font-size:11px; margin-top:10px; opacity:0.4;">დააჭირე დასაკოპირებლად</p>
            </div>
        </div>

        <div class="card" id="top-box">
            <h3 style="color:var(--gold); margin-top:0;">🏆 TOP 10 მხარდამჭერი</h3>
            <div id="leaderboard" style="font-size: 15px;">იტვირთება...</div>
        </div>
    </div>

    <audio id="bgMusic" loop src="https://www.soundhelix.com/examples/mp3/SoundHelix-Song-8.mp3"></audio>

    <script>
        function loginAction(type) {
            let name = type || document.getElementById('user-input').value;
            if(!name || name.trim().length < 2) {
                alert("გთხოვთ შეიყვანოთ სახელი!");
                return;
            }
            
            localStorage.setItem('nexus_session', name);
            
            // მუსიკის გააქტიურება
            const m = document.getElementById('bgMusic');
            m.play().then(() => {
                document.getElementById('music-btn').innerText = "🔊";
            }).catch(() => {});

            startApp();
        }

        function startApp() {
            const user = localStorage.getItem('nexus_session');
            if(user) {
                document.getElementById('login-overlay').style.display = 'none';
                document.getElementById('main-content').style.display = 'block';
                document.getElementById('user-greet').innerText = "მოგესალმები, " + user + "! 👋";
                loadData();
                updateTimer();
                setInterval(loadData, 5000);
                setInterval(updateTimer, 1000);
            }
        }

        window.onload = startApp;

        async function loadData() {
            try {
                const resp = await fetch('/api/data');
                const data = await resp.json();
                document.getElementById('bar').style.width = Math.min((data.total / 10000) * 100, 100) + '%';
                document.getElementById('total-val').innerText = data.total;
                
                let html = '';
                data.top.forEach((item, index) => {
                    html += `<div class="leader-item"><span>${index+1}. ${item.name}</span><span style="color:var(--gold); font-weight:bold;">${item.amount}₾</span></div>`;
                });
                document.getElementById('leaderboard').innerHTML = html || "მონაცემები არ არის";
            } catch (e) {}
        }

        function getFortune() {
            const fortunes = [
                "დღეს დიდი იღბალი გელის!", 
                "ვიღაც შენზე კარგს ფიქრობს! ✨", 
                "საუკეთესო დღეა ახალი საქმისთვის!", 
                "სურვილი, რომელსაც ეხლა ჩაიფიქრებ, აგისრულდება!", 
                "მოულოდნელი საჩუქარი გელის! 🎁",
                "შენი შრომა მალე დაფასდება!",
                "დღეს ყველაფერი შენს სასარგებლოდ მოხდება!"
            ];
            document.getElementById('fortune-text').innerText = fortunes[Math.floor(Math.random()*fortunes.length)];
            confetti({ particleCount: 150, spread: 70, origin: { y: 0.6 } });
            
            localStorage.setItem('nexus_fortune_last', new Date().getTime());
            updateTimer();
        }

        function updateTimer() {
            const last = localStorage.getItem('nexus_fortune_last');
            if (!last) return;

            const next = parseInt(last) + (24 * 60 * 60 * 1000);
            const diff = next - new Date().getTime();

            if (diff > 0) {
                document.getElementById('fortune-btn').style.display = 'none';
                document.getElementById('timer-box').style.display = 'block';
                const h = Math.floor(diff / 3600000).toString().padStart(2,'0');
                const m = Math.floor((diff % 3600000) / 60000).toString().padStart(2,'0');
                const s = Math.floor((diff % 60000) / 1000).toString().padStart(2,'0');
                document.getElementById('timer').innerText = `${h}:${m}:${s}`;
            } else {
                document.getElementById('fortune-btn').style.display = 'block';
                document.getElementById('timer-box').style.display = 'none';
            }
        }

        function copyIBAN() {
            navigator.clipboard.writeText('GE38BG0000000581620953');
            const toast = document.getElementById('toast');
            toast.classList.add('show');
            setTimeout(() => toast.classList.remove('show'), 3000);
        }

        function toggleMusic() {
            const m = document.getElementById('bgMusic');
            const btn = document.getElementById('music-btn');
            if (m.paused) { m.play(); btn.innerText = "🔊"; } 
            else { m.pause(); btn.innerText = "🔇"; }
        }
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
        return jsonify({'total': total, 'top': top})
    except: return jsonify({'total': 0, 'top': []})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
