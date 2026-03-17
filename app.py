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
    <title>NEXUS - მხარდაჭერა</title>
    <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.5.1/dist/confetti.browser.min.js"></script>
    <style>
        :root { --gold: #f6e05e; --orange: #ed8936; --dark: #0a0a0a; --card: #141414; }
        body { font-family: 'Segoe UI', system-ui, sans-serif; background: var(--dark); color: white; margin: 0; text-align: center; scroll-behavior: smooth; overflow-x: hidden; }
        
        /* ლოგინი */
        #login-overlay { position: fixed; inset: 0; background: var(--dark); z-index: 9999; display: flex; align-items: center; justify-content: center; }
        .login-card { background: var(--card); padding: 40px; border-radius: 30px; border: 1px solid var(--gold); width: 85%; max-width: 380px; box-shadow: 0 0 40px rgba(246, 224, 94, 0.1); }
        
        /* მენიუ */
        nav { background: rgba(0,0,0,0.9); padding: 15px; display: flex; justify-content: center; gap: 20px; position: sticky; top: 0; z-index: 100; border-bottom: 1px solid #222; backdrop-filter: blur(10px); }
        nav a { color: white; text-decoration: none; font-weight: bold; font-size: 14px; cursor: pointer; transition: 0.3s; }
        nav a:hover { color: var(--gold); }
        
        .container { max-width: 500px; margin: 20px auto; padding: 0 15px; display: none; } /* ლოგინამდე დამალულია */
        .card { background: var(--card); padding: 25px; border-radius: 25px; border: 1px solid #222; margin-bottom: 20px; position: relative; }
        
        .progress-bg { background: #000; height: 15px; border-radius: 20px; overflow: hidden; margin: 20px 0; border: 1px solid #333; }
        .progress-fill { background: linear-gradient(90deg, var(--gold), var(--orange)); height: 100%; width: 0%; transition: 2s ease-out; }
        
        .btn { background: var(--gold); color: black; border: none; padding: 16px; border-radius: 50px; font-size: 16px; font-weight: bold; cursor: pointer; transition: 0.3s; width: 100%; display: block; margin: 10px 0; }
        .btn:active { transform: scale(0.96); }
        
        .google-btn { background: white; color: #333; display: flex; align-items: center; justify-content: center; gap: 10px; }
        .input-style { background: #000; border: 1px solid #333; padding: 15px; border-radius: 15px; color: white; width: 100%; margin-bottom: 15px; box-sizing: border-box; text-align: center; }

        .music-control { position: fixed; bottom: 20px; left: 20px; background: rgba(0,0,0,0.8); width: 45px; height: 45px; border-radius: 50%; border: 1px solid var(--gold); cursor: pointer; z-index: 1000; display: flex; align-items: center; justify-content: center; }
        
        .leader-item { display: flex; justify-content: space-between; padding: 12px; border-bottom: 1px solid #222; }
    </style>
</head>
<body>

    <div id="login-overlay">
        <div class="login-card">
            <h2 style="color:var(--gold)">NEXUS CLUB</h2>
            <p style="opacity:0.7">გაიარეთ ავტორიზაცია</p>
            <input type="text" id="user-name" class="input-style" placeholder="თქვენი სახელი...">
            <button class="btn" onclick="finishLogin()">შესვლა ნომრით</button>
            <div style="margin:10px; opacity:0.3">ან</div>
            <button class="btn google-btn" onclick="finishLogin()">
                <img src="https://www.gstatic.com/images/branding/product/1x/gsa_512dp.png" width="20"> Google-ით შესვლa
            </button>
        </div>
    </div>

    <nav>
        <a onclick="window.scrollTo(0,0)">მთავარი</a>
        <a href="#rules-section">წესები</a>
        <a href="#top-section">TOP 10</a>
    </nav>

    <div class="music-control" onclick="toggleMusic()" id="music-btn">🔇</div>

    <div class="container" id="main-app">
        <h2 id="welcome-txt" style="color: var(--gold); font-size: 18px;">კეთილი იყოს შენი მობრძანება!</h2>

        <div class="card">
            <p style="margin:0; opacity: 0.6;">საერთო მიზანი</p>
            <h1 style="margin:10px 0; font-size: 35px; color: var(--gold);">10,000₾</h1>
            <div class="progress-bg"><div class="progress-fill" id="bar"></div></div>
            <p>სულ შეგროვდა: <span id="total-val" style="font-weight:bold; color:var(--gold)">0</span>₾</p>
        </div>

        <div class="card">
            <h3 style="margin-top:0;">✨ იღბლის წინასწარმეტყველება</h3>
            <div id="fortune-text" style="min-height: 50px; display:flex; align-items:center; justify-content:center; color: #ccc;">...</div>
            <button id="fortune-btn" class="btn" onclick="getFortune()">გამოცადე იღბალი</button>
            <div id="timer-box" style="display:none;">
                <p style="font-size:12px; opacity:0.5;">შემდეგი მცდელობა:</p>
                <div id="timer" style="font-weight:bold; color:var(--gold); font-size:20px;">00:00:00</div>
            </div>
        </div>

        <div class="card" id="rules-section">
            <h3 style="color:var(--gold); margin-top:0;">📜 საიტის წესები</h3>
            <div style="text-align: left; font-size: 14px; opacity: 0.8; line-height: 1.6;">
                1. მხარდაჭერა არის ნებაყოფლობითი.<br>
                2. იღბლის გამოცდა ხდება 24 საათში ერთხელ.<br>
                3. მონაცემები ახლდება ავტომატურად.<br>
                4. ტოპში მოსახვედრად მიუთითეთ სახელი.
            </div>
        </div>

        <div class="card">
            <p>მხარდასაჭერი IBAN (BOG):</p>
            <div style="background:#000; border:1px dashed var(--gold); padding:15px; border-radius:15px; cursor:pointer;" onclick="copyIBAN()">
                <strong style="color:var(--gold); letter-spacing:1px;">GE38BG0000000581620953</strong>
                <p style="font-size:10px; margin-top:5px; opacity:0.5;">დააკლიკე დასაკოპირებლად</p>
            </div>
        </div>

        <div class="card" id="top-section">
            <h3 style="color:var(--gold); margin-top:0;">🏆 TOP 10 მხარდამჭერი</h3>
            <div id="leaderboard">იტვირთება...</div>
        </div>
    </div>

    <audio id="bgMusic" loop src="https://www.soundhelix.com/examples/mp3/SoundHelix-Song-8.mp3"></audio>

    <script>
        let musicStarted = false;

        function finishLogin() {
            const name = document.getElementById('user-name').value || "სტუმარი";
            localStorage.setItem('nexus_user', name);
            
            // მუსიკის გააქტიურება ლოგინზე დაჭერისას
            const m = document.getElementById('bgMusic');
            m.play().then(() => {
                document.getElementById('music-btn').innerText = "🔊";
                musicStarted = true;
            }).catch(() => {});

            showApp();
        }

        function showApp() {
            const user = localStorage.getItem('nexus_user');
            if(user) {
                document.getElementById('login-overlay').style.display = 'none';
                document.getElementById('main-app').style.display = 'block';
                document.getElementById('welcome-txt').innerText = "გამარჯობა, " + user + "!";
                loadData();
                updateTimer();
            }
        }

        window.onload = showApp;

        async function loadData() {
            try {
                const resp = await fetch('/api/data');
                const data = await resp.json();
                document.getElementById('bar').style.width = Math.min((data.total / 10000) * 100, 100) + '%';
                document.getElementById('total-val').innerText = data.total;
                
                let html = '';
                data.top.forEach((item, index) => {
                    html += `<div class="leader-item"><span>${index+1}. ${item.name}</span><span style="color:var(--gold)">${item.amount}₾</span></div>`;
                });
                document.getElementById('leaderboard').innerHTML = html || "მონაცემები არ არის";
            } catch (e) {}
        }

        function getFortune() {
            const fortunes = ["დღეს დიდი იღბალი გელის!", "ვიღაც შენზე კარგს ფიქრობს", "საუკეთესო დღეა ახალი საქმისთვის", "სურვილი აგისრულდება!", "მოულოდნელი საჩუქარი გელის"];
            document.getElementById('fortune-text').innerText = fortunes[Math.floor(Math.random()*fortunes.length)];
            
            confetti({ particleCount: 150, spread: 70, origin: { y: 0.6 } });
            
            localStorage.setItem('fortune_time', new Date().getTime());
            updateTimer();
        }

        function updateTimer() {
            const last = localStorage.getItem('fortune_time');
            if (!last) return;

            const next = parseInt(last) + (24 * 60 * 60 * 1000);
            const now = new Date().getTime();
            const diff = next - now;

            if (diff > 0) {
                document.getElementById('fortune-btn').style.display = 'none';
                document.getElementById('timer-box').style.display = 'block';
                const h = Math.floor(diff / 3600000);
                const m = Math.floor((diff % 3600000) / 60000);
                const s = Math.floor((diff % 60000) / 1000);
                document.getElementById('timer').innerText = `${h}:${m}:${s}`;
                setTimeout(updateTimer, 1000);
            } else {
                document.getElementById('fortune-btn').style.display = 'block';
                document.getElementById('timer-box').style.display = 'none';
            }
        }

        function toggleMusic() {
            const m = document.getElementById('bgMusic');
            const btn = document.getElementById('music-btn');
            if (m.paused) { m.play(); btn.innerText = "🔊"; } 
            else { m.pause(); btn.innerText = "🔇"; }
        }

        function copyIBAN() {
            navigator.clipboard.writeText('GE38BG0000000581620953');
            alert("IBAN დაკოპირდა!");
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
