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
        :root { --gold: #f6e05e; --orange: #ed8936; --dark: #0a0a0a; }
        body { font-family: 'Segoe UI', sans-serif; background: var(--dark); color: white; margin: 0; text-align: center; scroll-behavior: smooth; }
        
        /* რეგისტრაციის ფანჯარა */
        #login-overlay { position: fixed; inset: 0; background: var(--dark); z-index: 2000; display: flex; align-items: center; justify-content: center; }
        .login-card { background: #111; padding: 40px; border-radius: 30px; border: 1px solid var(--gold); width: 80%; max-width: 350px; }
        
        nav { background: rgba(0,0,0,0.9); padding: 15px; display: flex; justify-content: center; gap: 20px; position: sticky; top: 0; z-index: 100; border-bottom: 1px solid #222; }
        nav a { color: white; text-decoration: none; font-weight: bold; font-size: 14px; cursor: pointer; }
        
        .container { max-width: 500px; margin: 20px auto; padding: 0 15px; }
        .card { background: #111; padding: 25px; border-radius: 25px; border: 1px solid #222; margin-bottom: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
        
        .progress-bg { background: #222; height: 25px; border-radius: 15px; overflow: hidden; margin: 15px 0; border: 1px solid #333; }
        .progress-fill { background: linear-gradient(90deg, var(--gold), var(--orange)); height: 100%; width: 0%; transition: 2s; }
        
        .btn { background: var(--gold); color: black; border: none; padding: 15px 35px; border-radius: 50px; font-size: 18px; font-weight: bold; cursor: pointer; transition: 0.3s; margin: 15px 0; width: 100%; }
        .btn:disabled { background: #444; color: #888; cursor: not-allowed; }
        
        .input-style { background: #222; border: 1px solid #444; padding: 15px; border-radius: 15px; color: white; width: 100%; margin-bottom: 10px; box-sizing: border-box; text-align: center; }
        
        .leader-item { display: flex; justify-content: space-between; padding: 12px; border-bottom: 1px solid #222; }
        .gold-text { color: var(--gold); font-weight: bold; }
        
        .music-control { position: fixed; bottom: 20px; left: 20px; background: rgba(0,0,0,0.7); padding: 10px; border-radius: 50%; cursor: pointer; z-index: 100; border: 1px solid var(--gold); }
        
        #rules-list { text-align: left; font-size: 14px; line-height: 1.6; color: #ccc; }
        #notif { position: fixed; top: 70px; right: -350px; background: var(--gold); color: black; padding: 15px 25px; border-radius: 15px; font-weight: bold; transition: 0.6s; z-index: 1000; }
    </style>
</head>
<body>

    <div id="login-overlay">
        <div class="login-card">
            <h2 style="color:var(--gold)">მოგესალმებით</h2>
            <p>გთხოვთ, შეიყვანოთ სახელი გასაგრძელებლად</p>
            <input type="text" id="user-name-input" class="input-style" placeholder="თქვენი სახელი...">
            <button class="btn" onclick="saveUser()">შესვლა</button>
        </div>
    </div>

    <nav>
        <a onclick="window.scrollTo(0,0)">მთავარი</a>
        <a href="#rules">წესები</a>
        <a href="#top">TOP 10</a>
    </nav>

    <div class="music-control" onclick="toggleMusic()" id="music-btn">🔇</div>
    <div id="notif">💰 ახალი მხარდამჭერი!</div>

    <div class="container">
        <h1 id="welcome-msg" style="color: var(--gold); font-size: 20px; margin-bottom: 20px;">გამარჯობა!</h1>

        <div class="card">
            <h2 style="margin:0;">მიზანი: <span class="gold-text">10,000₾</span></h2>
            <div class="progress-bg"><div class="progress-fill" id="bar"></div></div>
            <p>შეგროვდა: <span class="gold-text" id="total-val">0</span>₾</p>
        </div>

        <div class="card">
            <h1 style="font-size: 24px;">✨ იღბლის წინასწარმეტყველება</h1>
            <div id="fortune-text" style="min-height: 60px; font-size: 18px; margin: 15px 0; color: #ccc;">გაიგე შენი დღევანდელი ბედი...</div>
            <button id="fortune-btn" class="btn" onclick="getFortune()">გამოცადე იღბალი</button>
            <p id="cooldown-msg" style="font-size: 12px; color: #666; display: none;">შემდეგი ცდა ხვალ იქნება!</p>
        </div>

        <div class="card" id="rules">
            <h3 style="color:var(--gold)">📜 საიტის წესები</h3>
            <div id="rules-list">
                1. მხარდაჭერა არის ნებაყოფლობითი.<br>
                2. იღბლის გამოცდა შესაძლებელია დღეში მხოლოდ ერთხელ.<br>
                3. TOP 10-ში მოსახვედრად მიუთითეთ თქვენი სახელი ჩარიცხვისას.<br>
                4. იყავით პოზიტიურები! ✨
            </div>
        </div>

        <div class="card">
            <p>მხარდასაჭერი IBAN (BOG):</p>
            <div style="border: 2px dashed var(--gold); padding: 15px; border-radius: 15px; cursor: pointer;" onclick="copyIBAN()">
                <strong style="color:var(--gold); font-family:monospace;">GE38BG0000000581620953</strong>
                <p style="font-size:11px; margin-top:5px; opacity:0.7;">მიმღები: გ.ა | დანიშნულება: მხარდაჭერა</p>
            </div>
        </div>

        <div class="card" id="top">
            <h3 style="color:var(--gold); margin-top:0;">🏆 TOP 10 მხარდამჭერი</h3>
            <div id="leaderboard">იტვირთება...</div>
        </div>
    </div>

    <audio id="bgMusic" loop src="https://www.soundhelix.com/examples/mp3/SoundHelix-Song-17.mp3"></audio>
    <audio id="coinSound" src="https://www.soundjay.com/misc/sounds/coin-drop-1.mp3"></audio>

    <script>
        let lastCount = 0;

        function saveUser() {
            const name = document.getElementById('user-name-input').value;
            if(name.length > 1) {
                localStorage.setItem('username', name);
                document.getElementById('login-overlay').style.display = 'none';
                document.getElementById('welcome-msg').innerText = "გამარჯობა, " + name + "!";
            } else { alert("გთხოვთ შეიყვანოთ სახელი"); }
        }

        window.onload = () => {
            const savedName = localStorage.getItem('username');
            if(savedName) {
                document.getElementById('login-overlay').style.display = 'none';
                document.getElementById('welcome-msg').innerText = "გამარჯობა, " + savedName + "!";
            }
            checkCooldown();
            loadData();
        };

        function checkCooldown() {
            const lastFortune = localStorage.getItem('lastFortuneDate');
            if (lastFortune === new Date().toDateString()) {
                document.getElementById('fortune-btn').disabled = true;
                document.getElementById('cooldown-msg').style.display = 'block';
                document.getElementById('fortune-text').innerText = "დღევანდელი იღბალი უკვე ნახე! ✨";
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
                    html += `<div class="leader-item"><span>${index+1}. ${item.name}</span><span class="gold-text">${item.amount}₾</span></div>`;
                });
                document.getElementById('leaderboard').innerHTML = html || "ჯერ არავინ არის...";
                if (data.count > lastCount && lastCount !== 0) { showNotif(); }
                lastCount = data.count;
            } catch (e) {}
        }

        function getFortune() {
            const f = [
                "დღეს დიდი იღბალი გელის!", "ვიღაც შენზე კარგს ფიქრობს", "დღეს ყველაფერი გამოგივა!", 
                "მალე სასიხარულო ამბავს გაიგებ", "მოულოდნელი საჩუქარი გელის!", "შენი ოცნება მალე ასრულდება",
                "დღეს იდეალური დღეა ახალი საქმისთვის", "ბედნიერება შენსკენ მოემართება", "ენერგიით სავსე დღე გექნება",
                "დღეს ბევრს გაიცინებ!", "იღბალი შენს მხარესაა", "შენი შრომა მალე დაფასდება",
                "დღეს საინტერესო ადამიანს შეხვდები", "სამყარო გიღიმის!", "წინ დიდი წარმატებაა",
                "დღეს შენი დღეა!", "სურვილი ჩაიფიქრე, აგისრულდება", "სიხარული კარზე მოგადგება"
            ];
            const result = f[Math.floor(Math.random()*f.length)];
            document.getElementById('fortune-text').innerText = result;
            confetti({ particleCount: 100, spread: 70 });
            localStorage.setItem('lastFortuneDate', new Date().toDateString());
            setTimeout(checkCooldown, 2000);
        }

        function toggleMusic() {
            const m = document.getElementById('bgMusic');
            const btn = document.getElementById('music-btn');
            if (m.paused) { m.play(); btn.innerText = "🔊"; } 
            else { m.pause(); btn.innerText = "🔇"; }
        }

        function copyIBAN() {
            navigator.clipboard.writeText('GE38BG0000000581620953');
            alert('IBAN კოპირებულია!');
        }

        function showNotif() {
            const n = document.getElementById('notif');
            document.getElementById('coinSound').play();
            n.style.right = '20px';
            setTimeout(() => n.style.right = '-350px', 5000);
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
