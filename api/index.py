from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def home():
    return "<h1>Plato Vercel Backend is Live! 🚀</h1>"

@app.route('/api/verify', methods=['POST'])
def verify_user():
    def get_headers(is_json=False):
        h = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Mobile Safari/537.36',
            'Accept': 'application/json' if is_json else 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
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
        if 'ticket=' in full_url:
            ticket = full_url.split('ticket=')[1].split('&')[0]
        elif 'd=' in full_url:
            ticket = full_url.split('d=')[1].split('&')[0]
        else:
            return jsonify({"success": False, "message": "Link me Ticket nahi mila."})

        session = requests.Session()
        
        # Step 1: Init (Cookies)
        # Vercel functions have a 10s timeout, usually enough for these 3 calls
        init_url = f"https://auth.platorelay.com/a?d={ticket}"
        session.get(init_url, headers=get_headers(False), timeout=4)
        
        # Step 2: Validate
        step2_url = f"https://auth.platorelay.com/api/session/step?ticket={ticket}&service=2"
        payload = {
            "captcha": None,
            "meta": "49080eaf479094074f9aef00135c724d774d00f2aeb7dd05bf6e1507bf2c8777d5bd4f2e817e324382ef71c9063d68d9dcaad9f48c98179b6db8553aa273be201b5cd2cd6e3a11ccf6b46a1de57ef91f3472c46c427351e78c56ba5b2ce9eb0b7319e91f5e3c8a8d189106337564468e2d7989dd250f6f738f536e4a72c1f6aa70a90a96da5d095601017e8bc7e97b1501d6b47fdbec739462bf938dc1443af6597570a677d9430d8aeadc353cbf526d61ea1433dc75aa683e8d99121e54320774e24c89952bea664ff9352e7d96fe6bd89f95b534d424ea5edea614145b2779844d16329d9143103a6044b3f1da49c2eee1f980449cfa20058685f821f55a98fc1007dac7f03aa3a4424550b25e8ed45c7431c13e217c067a4e8c12906f3fdc426cfb68f049568caa290a6b893a83cb2b51491b7aa7b48119cbc2d09caed2c1c918facca14346601039dabbae1c68313893e759467b6b7199bd83f61f5f491bafd56f79a940d47d04e1ce50c45c7ec0e91f3b341304fe0925204619c4b77504d03c6fa37412b74ce654ec417b2cfe6185ce97cfe6bb086ef2d4315af09acab36337e5ac61fc450942b057bf7244be2647701540c0b9019d33e3e556978e0c648f54100462a545418ff18d4b8c814527bf482f586f79fe2ca447aa4d18fd9c32b9bcdbda710609b3576e4b4076713972cfcdc25d186b57240ec61f6e8841a5a6bd7da343959631cd8010bdcac1ec6a8a48a2cb3a8b8f2e6f97c0f32a60e30cf219b40d807afb10e01fa3ef5ea44d61c774ef4d98f9de1a159794dcc1d191e975bdb54ceab325622ea147191d1a5209899862bee649f190bae8d9b979751c060143880d2dda779801cdba5c6e82d56b44dbf6074e03c333ad4a6c1584f3ace235de2adc3be1a7d2422987b22641e879aa29722ce77e45831038f5074646b63ca8e211",
            "stream": "183cf7f7c7e4985a48c81cd5b05a3fb72cea4cdf730a6075097dbce210bac5c328e8ccb80c15e57d40c371e6167f6ac3fb38efd4ad37734c6260f34f26b7703011",
            "resolved": True
        }
        
        session.put(step2_url, headers=get_headers(True), json=payload, timeout=4)
        
        # Step 3: Status
        status_url = f"https://auth.platorelay.com/api/session/status?ticket={ticket}"
        step3 = session.get(status_url, headers=get_headers(False), timeout=4)
        
        try:
            return jsonify({
                "success": True, 
                "plato_response": step3.json(),
                "message": "Verification Successful"
            })
        except:
             return jsonify({
                "success": False, 
                "plato_response": step3.text,
                "message": "Response not JSON"
            })

    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

# Vercel ko ye line chahiye hoti hai
app = app
