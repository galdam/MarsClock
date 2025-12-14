import network, json, time
import socket



def start_web_server():
    addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
    s = socket.socket()
    s.bind(addr)
    s.listen(1)

    print('Listening on', addr)

    while True:
        cl, addr = s.accept()
        handle_client(cl)

def handle_client(cl):
    request = b""
    while True:
        chunk = cl.recv(1024)
        if not chunk:
            break
        request += chunk
        if b"\r\n\r\n" in request:
            # Header/body separator found
            header_end = request.find(b"\r\n\r\n") + 4
            headers = request[:header_end].decode()
            break

    # Parse headers
    content_length = 0
    for line in headers.split("\r\n"):
        if line.lower().startswith("content-length:"):
            content_length = int(line.split(":")[1].strip())

    # Read remaining body bytes if needed
    body = request[header_end:]
    while len(body) < content_length:
        body += cl.recv(1024)

    body_str = body.decode()

    if "POST /save" in headers:
        params = parse_post_data(body_str)
        save_config(params)
        response = html_page("Settings saved!")
    else:
        response = html_page()

    cl.send('HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n')
    cl.send(response)
    cl.close()



def html_page(message=""):
    return f"""<!DOCTYPE html>
<html>
    <head>
        <title>Pico Configuration</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
    </head>
    <body>
        <h2>Pico Configuration</h2>
        <p>{message}</p>
        <form action="/save" method="post">
            WiFi SSID: <input type="text" name="ssid"><br>
            WiFi Password: <input type="text" name="password"><br>
            <input type="submit" value="Save">
        </form>
    </body>
</html>
"""


def html_page(message=""):
    return f"""<!DOCTYPE html>
<html>
<head>
    <title>Pico Configuration</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {{ font-family: sans-serif; margin: 20px; }}
        h2 {{ color: #2c3e50; }}
        .section {{ margin-bottom: 30px; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; }}
        th {{ background-color: #f2f2f2; }}
        input[type=text], input[type=date], input[type=number] {{
            width: 95%; padding: 5px; margin: 3px 0;
        }}
        button {{ padding: 5px 10px; margin-top: 10px; }}
        .msg {{ color: green; font-weight: bold; }}
    </style>
    <script>
        function addBirthdayRow() {{
            const table = document.getElementById('birthdays');
            const row = table.insertRow();
            row.innerHTML = `
                <td><input type="text" name="name" placeholder="Name"></td>
                <td><input type="date" name="birthday"></td>
                <td><button type="button" onclick="removeRow(this)">Remove</button></td>
            `;
        }}

        function addLocationRow() {{
            const table = document.getElementById('locations');
            const row = table.insertRow();
            row.innerHTML = `
                <td><input type="text" name="place" placeholder="Place name"></td>
                <td><input type="number" step="any" name="longitude" placeholder="Longitude"></td>
                <td><input type="number" step="any" name="latitude" placeholder="Latitude"></td>
                <td><button type="button" onclick="removeRow(this)">Remove</button></td>
            `;
        }}

        function removeRow(btn) {{
            const row = btn.parentNode.parentNode;
            row.parentNode.removeChild(row);
        }}
    </script>
</head>
<body>
    <h2>Pico Configuration</h2>
    <p class="msg">{message}</p>

    <form action="/save" method="post">

        <div class="section">
            <h3>Birthdays</h3>
            <table id="birthdays">
                <tr><th>Name</th><th>Birthday (YYYY-MM-DD)</th><th></th></tr>
            </table>
            <button type="button" onclick="addBirthdayRow()">Add Birthday</button>
        </div>

        <div class="section">
            <h3>Locations</h3>
            <table id="locations">
                <tr><th>Place</th><th>Longitude</th><th>Latitude</th><th></th></tr>
            </table>
            <button type="button" onclick="addLocationRow()">Add Location</button>
        </div>

        <input type="submit" value="Save Settings">
    </form>
</body>
</html>
"""


import re  # MicroPython regex module

def parse_post_data(body):
    params = {}
    for pair in body.split('&'):
        if '=' in pair:
            key, value = pair.split('=', 1)
            key = re.sub('%([0-9A-Fa-f]{2})', lambda m: chr(int(m.group(1), 16)), key)
            value = re.sub('%([0-9A-Fa-f]{2})', lambda m: chr(int(m.group(1), 16)), value)
            params[key] = value.replace('+', ' ')
    return params

__ = '''
def parse_post_data(body):
    params = {}
    pairs = body.split('&')
    for pair in pairs:
        if '=' in pair:
            key, value = pair.split('=', 1)
            params[key] = value.replace('+', ' ')
    return params
'''

def save_config(params):
    with open('config.json', 'w') as f:
        json.dump(params, f)
    print("Config saved:", params)
    

#import network
#from pico_config import start_web_server  # if saved in pico_config.py
if __name__ == "__main__":
    ap = network.WLAN(network.AP_IF)
    ap.config(essid='PicoConfig', password='12345678')
    ap.active(True)
    print('AP IP:', ap.ifconfig()[0])

    start_web_server()
    print('Done')
