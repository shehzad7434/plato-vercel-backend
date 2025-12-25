from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import time
import json

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def home():
    return "<h1>Plato Backend V3 (Chrome 144) is Live! 🚀</h1>"

@app.route('/api/verify', methods=['POST'])
def verify_user():
    # --- HEADERS FROM YOUR LATEST LOGS ---
    def get_headers(is_json=False):
        h = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Mobile Safari/537.36',
            'Accept': 'application/json' if is_json else 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'x-client-name': 'platoboost webclient',
            'x-client-version': '5.3.2',
            'sec-ch-ua-platform': '"Android"',
            'sec-ch-ua': '"Not(A:Brand";v="8", "Chromium";v="144", "Google Chrome";v="144"',
            'sec-ch-ua-mobile': '?1',
            'origin': 'https://auth.platorelay.com',
            'referer': 'https://auth.platorelay.com/',
            'priority': 'u=1, i'
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
            return jsonify({"success": False, "message": "Invalid Link."})

        session = requests.Session()
        
        # --- STEP 1: INITIALIZE SESSION (Cookies) ---
        init_url = f"https://auth.platorelay.com/a?d={ticket}"
        session.get(init_url, headers=get_headers(False), timeout=5)
        
        # --- STEP 2: BYPASS ATTEMPT (PUT Request) ---
        step2_url = f"https://auth.platorelay.com/api/session/step?ticket={ticket}&service=2"
        
        # NOTE: 'meta' string dynamic hoti hai. Hum purani wali use nahi kar sakte.
        # Hum 'None' bhej kar try karenge agar server allow karta hai.
        payload = {
            "captcha": None,
            "meta": None, 
            "resolved": True
        }
        
        # Bypass Request
        session.put(step2_url, headers=get_headers(True), json=payload, timeout=5)
        
        # --- STEP 3: CHECK STATUS ---
        status_url = f"https://auth.platorelay.com/api/session/status?ticket={ticket}"
        step3 = session.get(status_url, headers=get_headers(False), timeout=5)
        
        try:
            json_response = step3.json()
            
            # Check if Key is present
            key = json_response.get('data', {}).get('key')
            
            if key and "KEY_" in key:
                 return jsonify({
                    "success": True, 
                    "plato_response": json_response,
                    "message": "Key Found!"
                })
            else:
                # Agar key nahi mili, toh matlab user ko manually verify karna padega
                return jsonify({
                    "success": True, 
                    "plato_response": json_response,
                    "message": "Key Not Found (Redirect Needed)"
                })

        except:
             return jsonify({
                "success": False, 
                "plato_response": step3.text,
                "message": "Response Error"
            })

    except Exception as e:
        return jsonify({"success": False, "message": str(e)})
