from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import time
import random

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def home():
    return "<h1>Plato Vercel Backend V2 is Live! 🚀</h1>"

@app.route('/api/verify', methods=['POST'])
def verify_user():
    # Headers - Browser jaise dikhne ke liye
    def get_headers(is_json=False):
        h = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
            'Accept': 'application/json' if is_json else 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'x-client-name': 'platoboost webclient',
            'x-client-version': '5.3.2',
            'sec-ch-ua-platform': '"Android"',
            'sec-ch-ua-mobile': '?1',
            'origin': 'https://auth.platorelay.com',
            'referer': 'https://auth.platorelay.com/'
        }
        if is_json:
            h['Content-Type'] = 'application/json'
        return h

    try:
        data = request.json
        full_url = data.get('url')
        
        ticket = ""
        # Link Parsing Logic
        if 'ticket=' in full_url:
            ticket = full_url.split('ticket=')[1].split('&')[0]
        elif 'd=' in full_url:
            ticket = full_url.split('d=')[1].split('&')[0]
        else:
            return jsonify({"success": False, "message": "Link invalid hai. Sahi Delta link daalo."})

        session = requests.Session()
        
        # --- STEP 1: Link Visit (Cookie Banana) ---
        init_url = f"https://auth.platorelay.com/a?d={ticket}"
        session.get(init_url, headers=get_headers(False), timeout=5)
        
        # Thoda sa delay taaki real user lage
        time.sleep(1)

        # --- STEP 2: Validation (Bypass Attempt) ---
        # Note: Delta ka service ID kabhi kabhi change hota hai (1, 2, 10).
        # Hum generic bypass try kar rahe hain bina heavy meta data ke.
        step2_url = f"https://auth.platorelay.com/api/session/step?ticket={ticket}&service=2"
        
        # Payload ko simple rakha hai taaki signature match ka issue na ho
        payload = {
            "captcha": None,
            "resolved": True
        }
        
        session.put(step2_url, headers=get_headers(True), json=payload, timeout=5)
        
        # --- STEP 3: Status Check ---
        status_url = f"https://auth.platorelay.com/api/session/status?ticket={ticket}"
        step3 = session.get(status_url, headers=get_headers(False), timeout=5)
        
        try:
            json_response = step3.json()
            
            # Agar 'minutesLeft' 0 hai, matlab bypass fail hua ya link expire hai
            if json_response.get('data', {}).get('minutesLeft', 0) == 0:
                 return jsonify({
                    "success": True, 
                    "plato_response": json_response,
                    "message": "Link Valid hai par Bypass fail hua. (Security Patch)"
                })

            return jsonify({
                "success": True, 
                "plato_response": json_response,
                "message": "Verification Successful"
            })
        except:
             return jsonify({
                "success": False, 
                "plato_response": step3.text,
                "message": "Response JSON nahi hai (Server Error)"
            })

    except Exception as e:
        return jsonify({"success": False, "message": str(e)})
