import os
from flask import Flask, render_template_string, request, jsonify
from supabase import create_client, Client

app = Flask(__name__)

# --- მონაცემები ---
# აქ ჩასვი შენი Project URL (Settings -> API-ში რომ არის)
SUPABASE_URL = "აქ_ჩასვი_შენი_URL" 
SUPABASE_KEY = "sb_publishable_Y18wbjUAhW7gWfFORJn-wQ_EQs8ZB_2"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ka">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ZELO - მხარდაჭერა & იღბალი</title>
    <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.5.1/dist/confetti.browser.min.js"></script>
    <style>
        :root { --gold: #f6e05e; --purple: #6b46c1; --dark: #0a0a0a; }
        body { font-family: 'Segoe UI', sans-serif; background: var(--dark); color: white; margin: 0; text-align: center; }
        nav { background: rgba(0,0,0,0.8); padding: 15px; display: flex; justify-content: center; gap: 20px; position: sticky; top: 0; z-index: 100; }
        nav a { color: white; text-decoration: none; font-weight: bold; font-size: 14px; }
        .container { max-width: 500px; margin: 20px auto; padding: 0 15px; }
        .card { background: #111; padding: 25px; border-radius: 25px; border: 1px solid #222; margin-bottom: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
        
        .progress-bg { background: #222; height: 25px; border-radius: 15px; overflow: hidden; margin: 15px 0; border: 1px solid #333; }
        .progress-fill { background: linear-gradient(90deg, #f6e05e, #ed8936); height: 100%; width: 0%; transition: 2s cubic-bezier(0.1, 0, 0.1, 1); }
        
        .leader-item { display: flex; justify-content: space-between; padding: 12px; border-bottom: 1px solid #222; font-size: 16px; }
        .leader-item:last-child { border: none; }
        .gold-text { color: var(--gold); font-weight: bold; }
        
        .btn { background: var(--gold); color: black; border: none; padding: 15px 35px; border-radius: 50px; font-size: 18px; font-weight: bold; cursor: pointer; transition: 0.3s; margin: 15px 0; }
        .btn:active { transform: scale(0.95); }
        
        .iban-box { border: 2px dashed var(--gold); padding: 15px; border-radius: 15px; margin: 20px 0; cursor: pointer; background: rgba(246, 224, 94, 0.05); }
        #notif { position: fixed; top: 70px; right: -350px; background: var(--gold); color: black; padding: 15px 25px; border-radius: 15px; font-weight: bold; transition: 0.6s; z-index: 1000; box-shadow: 0 5px 20px rgba(0,0,0,0.4); }
    </style>
</head>
<body>
    <nav><a href="#">მთავარი</a><a href="#rules">წესები</a><a href="#top">TOP 10</a></nav>
    <div id="notif">💰 ახალი დონაცია!</div>

    <div class="container">
        <div class="card">
            <h2 style="margin:0;">მიზანი: <span class="gold-text">10,000₾</span></h2>
            <div class="progress-bg"><div class="progress-fill" id="bar"></div></div>
            <p>სულ შეგროვდა: <span class="gold-text" id="total-val">0</span>₾</p>
        </div>

        <div class="card">
            <h1 style="font-size: 24px;">✨ იღბლის წინასწარმეტყველება</h1>
            <div id="fortune-text" style="min-height: 60px; font-size: 18px; margin: 15px 0; color: #ccc;">დააჭირე ღილაკს და გაიგე შენი ბედი...</div>
            <button class="btn" onclick="getFortune()">გამოცადე იღბალი</button>
        </div>

        <div class="card">
            <p style="margin-bottom: 5px;">მხარდასაჭერი IBAN (BOG):</p>
            <div class="iban-box" onclick="copyIBAN()">
                <strong style="color:var(--gold); font-size:15px; font-family:monospace;">GE38BG0000000581620953</strong>
                <p style="font-size:11px; margin:5px 0 0 0; opacity:0.7;">მიმღები: გ.ა | მიზანი: მხარდაჭერა</p>
            </div>
            <p style="font-size: 12px; color: #666;">ჩარიცხვის შემდეგ თქვენი სახელი გამოჩნდება ტოპში!</p>
        </div>

        <div class="card" id="top">
            <h3 style="color:var(--gold); margin-top:0;">🏆 TOP 10 მხარდამჭერი</h3>
            <div id="leaderboard">იტვირთება...</div>
        </div>
    </div>

    <audio id="coinSound" src="https://www.soundjay.com/misc/sounds/coin-drop-1.mp3"></audio>

    <script>
        let lastCount = 0;

        async function loadData() {
            try {
                const resp = await fetch('/api/data');
                const data = await resp.json();
                
                // პროგრეს ბარი
                const percent = Math.min((data.total / 10000) * 100, 100);
                document.getElementById('bar').style.width = percent + '%';
                document.getElementById('total-val').innerText = data.total;

                // ლიდერბორდი
                let html = '';
                data.top.forEach((item, index) => {
                    html += `<div class="leader-item"><span>${index+1}. ${item.name}</span><span class="gold-text">${item.amount}₾</span></div>`;
                });
                document.getElementById('leaderboard').innerHTML = html || "ჯერ არავინ არის...";

                // შეტყობინება თუ ახალი დაემატა
                if (data.count > lastCount && lastCount !== 0) {
                    showNotif();
                }
                lastCount = data.count;
            } catch (e) { console.log("ბაზასთან კავშირი ვერ დამყარდა"); }
        }

        function showNotif() {
            const n = document.getElementById('notif');
            document.getElementById('coinSound').play();
            n.style.right = '20px';
            confetti({ particleCount: 150, spread: 70, origin: { y: 0.6 } });
            setTimeout(() => { n.style.right = '-350px'; }, 5000);
        }

        function getFortune() {
            const f = ["დღეს დიდი იღბალი გელის!", "ბანკომატთან სიურპრიზი დაგხვდება", "ვიღაც შენზე კარგს ფიქრობს", "დღეს ყველაფერი გამოგივა!"];
            document.getElementById('fortune-text').innerText = f[Math.floor(Math.random()*f.length)];
            confetti({ particleCount: 50, spread: 50 });
        }

        function copyIBAN() {
            navigator.clipboard.writeText('GE38BG0000000581620953');
            alert('IBAN კოპირებულია! გაიხარე!');
        }

        setInterval(loadData, 5000);
        loadData();
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/data')
def get_data():
    try:
        res = supabase.table('donations').select('*').execute()
        items = res.data
        total = sum(item['amount'] for item in items)
        top = sorted(items, key=lambda x: x['amount'], reverse=True)[:10]
        return jsonify({'total': total, 'top': top, 'count': len(items)})
    except:
        return jsonify({'total': 0, 'top': [], 'count': 0})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
