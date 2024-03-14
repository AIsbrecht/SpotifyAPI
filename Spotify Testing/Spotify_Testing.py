import requests
from flask import Flask, redirect, request, jsonify, session, render_template
from datetime import datetime, timedelta
import urllib.parse

app = Flask(__name__)

app.secret_key = '53d355f8-571a-4590-a310-1f9579440851'

CLIENT_ID= 'a00cd7494a1740288da72ba5033f7a19'
CLIENT_SECRET = '3c67018571e543ed88f5138c69810afd'

REDIRECT_URI = 'http://127.0.0.1:8080'

AUTH_URL = 'https://accounts.spotify.com/authorize'
TOKEN = 'https://accounts.spotify.com/api/token'
API_BASE_URL ='https://api.spotify.com/v1/'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    scope = "user-read-private user_read_email"
    params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "scope": scope,
        "redirect_uri": REDIRECT_URI,
        "show_dialog": False
    }
    auth_url = f"{AUTH_URL}?{urllib.parse.urlencode(params)}"
    return render_template('login.html', auth_url=auth_url)


@app.route('/callback')
def callback():
    if 'error' in request.args:
        return jsonify({"error": request.args['error']})

    
    if 'code' in request.args:
        req_body = {
            'code': request.args['code'],
            'grant_type': 'authorization_code',
            'redirect_uri': REDIRECT_URI,
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET
        }
        
        response = requests.post(TOKEN, data=req_body)
        token_info = response.json()

        session['access_token'] = token_info['access_token']
        session['refresh_token'] = token_info['refresh_token']
        session['expires_at'] = datetime.now().timestamp() + token_info['expires_in']

        return redirect('/playlists')

@app.route('/playlists')
def get_playlists():
    if 'access_token' not in session:
        return redirect('/login')

    if datetime.now.timestamp() > session['expires_at']:
        return redirect('/refresh_token')

    headers = {
        'Authorization': f"Bearer {session['access_token']}"
    }

    response = requests.get(API_BASE_URL + 'me/playlists', headers=headers)
    playlists = response.json()

    return jsonify(playlists)

@app.route('/refresh_token')

def refresh_token():
    if 'refresh_token' not in session:
        return redirect('/login')

    if datetime.now().timestamp() > session['expires_at']:
        req_body = {
            'grant_type': 'refresh_token',
            'refresh_token': session['refresh_token'],
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET
        }
   
        response  = requests.post(TOKEN, data=req_body)
        new_token_info = response.json()

        session['access_token'] = new_token_info['access_token']
        session['expires_at'] = datetime.now().timestamp() + new_token_info['expires_in']

        return redirect('/playlists')


if __name__ == '__main__':
    print("starting up")
    app.run(host='127.0.0.1', port = 8080, debug=True)