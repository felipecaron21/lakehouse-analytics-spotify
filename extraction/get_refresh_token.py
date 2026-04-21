"""
Run this script ONCE to generate a Spotify refresh token.
It will open the browser for login, then save the token to .env
"""
import os
import webbrowser
import urllib.parse
import http.server
import threading
import requests
from dotenv import load_dotenv, set_key

load_dotenv()

CLIENT_ID = os.environ["SPOTIFY_CLIENT_ID"]
CLIENT_SECRET = os.environ["SPOTIFY_CLIENT_SECRET"]
REDIRECT_URI = "http://127.0.0.1:8888"
SCOPE = "playlist-read-private playlist-read-collaborative"
ENV_FILE = os.path.join(os.path.dirname(__file__), "..", ".env")

auth_code = None


class CallbackHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        global auth_code
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)
        auth_code = params.get("code", [None])[0]
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"<h2>Auth OK! Pode fechar esta aba.</h2>")

    def log_message(self, *args):
        pass


def start_server():
    server = http.server.HTTPServer(("127.0.0.1", 8888), CallbackHandler)
    server.handle_request()


print("Abrindo navegador para autenticação no Spotify...")
params = urllib.parse.urlencode({
    "client_id": CLIENT_ID,
    "response_type": "code",
    "redirect_uri": REDIRECT_URI,
    "scope": SCOPE,
})
webbrowser.open(f"https://accounts.spotify.com/authorize?{params}")

thread = threading.Thread(target=start_server)
thread.start()
thread.join(timeout=120)

if not auth_code:
    print("Timeout: nenhum código recebido. Tente novamente.")
    exit(1)

response = requests.post(
    "https://accounts.spotify.com/api/token",
    data={
        "grant_type": "authorization_code",
        "code": auth_code,
        "redirect_uri": REDIRECT_URI,
    },
    auth=(CLIENT_ID, CLIENT_SECRET),
)
response.raise_for_status()
tokens = response.json()

refresh_token = tokens["refresh_token"]
set_key(ENV_FILE, "SPOTIFY_REFRESH_TOKEN", refresh_token)
print(f"Refresh token salvo no .env com sucesso!")
