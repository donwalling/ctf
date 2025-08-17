
import http.server, socketserver, os

PORT = 8008

class Handler(http.server.SimpleHTTPRequestHandler):
    def translate_path(self, path):
        root = os.getcwd()
        path = path.split('?',1)[0].split('#',1)[0]
        path = path.lstrip('/')
        return os.path.join(root, path)

def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    with socketserver.ThreadingTCPServer(("", PORT), Handler) as httpd:
        print(f"Serving dashboard on http://localhost:{PORT}/dashboard/index.html")
        print("Tip: run `ctf-sim --delay 0.2` (or `python simulate.py`) to update logs/state.json")
        httpd.serve_forever()

if __name__ == "__main__":
    main()
