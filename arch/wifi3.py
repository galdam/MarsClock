import machine, network, socket, json, re  

from machine import RTC

USER_CONFIG_FILE = "user_config.json"


# ---------- CONFIG MANAGEMENT ----------
__ = '''
def save_config(params):
    with open(USER_CONFIG_FILE, 'w') as f:
        json.dump(params, f)
    print("Config saved:", params)
'''

def load_config():
    try:
        with open("user_config.json") as f:
            return json.load(f)
    except:
        return {"birthdays": [], "locations": [], "selectedlocation": ""}

# ---------- HTML PAGE ----------
def html_page(message="", config=None):
    if config is None:
        config = load_config()

    # Build existing birthday rows
    birthday_rows = ""
    for b in config.get("birthdays", []):
        birthday_rows += f"""
            <tr>
                <td><input type="text" name="bname" value="{b.get('name','')}" placeholder="Name"></td>
                <td><input type="date" name="bdate" value="{b.get('date','')}"></td>
                <td><button type="button" onclick="removeRow(this)">Remove</button></td>
            </tr>
        """

    # Build existing location rows
    location_rows = ""
    for loc in config.get("locations", []):
        checked = "checked" if loc.get("name") == config.get("selectedlocation") else ""
        location_rows += f"""
            <tr>
                <td><input type="radio" name="selectedlocation" value="{loc.get('name','')}" {checked}></td>
                <td><input type="text" name="lname" value="{loc.get('name','')}" placeholder="Place"></td>
                <td><input type="number" step="any" name="longitude" value="{loc.get('longitude','')}" placeholder="Longitude"></td>
                <td><input type="number" step="any" name="latitude" value="{loc.get('latitude','')}" placeholder="Latitude"></td>
                <td><button type="button" onclick="removeRow(this)">Remove</button></td>
            </tr>
        """


    return f"""<!DOCTYPE html>
<html>
<head>
    <title>Mars Clock Configuration</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {{ font-family: sans-serif; margin: 20px; }}
        h2 {{ color: #2c3e50; }}
        table {{ border-collapse: collapse; width: 100%; margin-bottom: 10px; }}
        th, td {{ border: 1px solid #ccc; padding: 6px; text-align: left; }}
        th {{ background-color: #f0f0f0; }}
        button {{ padding: 4px 8px; }}
        .msg {{ color: green; font-weight: bold; }}
    </style>
    <script>
        function addBirthdayRow() {{
            const table = document.getElementById('birthdays');
            const row = table.insertRow();
            row.innerHTML = `
                <td><input type="text" name="bname" placeholder="Name"></td>
                <td><input type="date" name="bdate"></td>
                <td><button type="button" onclick="removeRow(this)">Remove</button></td>
            `;
        }}

        function addLocationRow() {{
            const table = document.getElementById('locations');
            const row = table.insertRow();
            row.innerHTML = `
                <td><input type="radio" name="selectedlocation" value=""></td>
                <td><input type="text" name="lname" placeholder="Place" oninput="updateRadioValue(this)"></td>
                <td><input type="number" step="any" name="longitude" placeholder="Longitude"></td>
                <td><input type="number" step="any" name="latitude" placeholder="Latitude"></td>
                <td><button type="button" onclick="removeRow(this)">Remove</button></td>
            `;
        }}

        function updateRadioValue(input) {{
            const row = input.closest('tr');
            const radio = row.querySelector('input[type=radio]');
            if (radio) radio.value = input.value;
        }}

        function removeRow(btn) {{
            const row = btn.closest('tr');
            row.parentNode.removeChild(row);
        }}

        function setClientTime() {{
            const now = new Date();
            const formattedUTC = now.getUTCFullYear() + "-" +
                String(now.getUTCMonth() + 1).padStart(2, '0') + "-" +
                String(now.getUTCDate()).padStart(2, '0') + "T" +
                String(now.getUTCHours()).padStart(2, '0') + ":" +
                String(now.getUTCMinutes()).padStart(2, '0') + ":" +
                String(now.getUTCSeconds()).padStart(2, '0') + "Z";
        }}

        // before submit, capture current time
        function prepareForm() {{
            setClientTime();
            return true;
        }}

        function setClientUTCTime(targetId) {{
            const now = new Date();
            const formatted = now.getUTCFullYear() + "-" +
                            String(now.getUTCMonth()+1).padStart(2, '0') + "-" +
                            String(now.getUTCDate()).padStart(2, '0') + "T" +
                            String(now.getUTCHours()).padStart(2, '0') + ":" +
                            String(now.getUTCMinutes()).padStart(2, '0') + ":" +
                            String(now.getUTCSeconds()).padStart(2, '0') + "Z";
            document.getElementById(targetId).value = formatted;
        }}

        function prepareForm() {{
            // Handle both hidden fields if they exist
            const timeFields = document.querySelectorAll("input[id^='client_time']");
            const now = new Date();
            const formatted = now.getUTCFullYear() + "-" +
                            String(now.getUTCMonth()+1).padStart(2, '0') + "-" +
                            String(now.getUTCDate()).padStart(2, '0') + "T" +
                            String(now.getUTCHours()).padStart(2, '0') + ":" +
                            String(now.getUTCMinutes()).padStart(2, '0') + ":" +
                            String(now.getUTCSeconds()).padStart(2, '0') + "Z";
            timeFields.forEach(f => f.value = formatted);
            return true;
        }}
    </script>
</head>
<body>
    <h2>Mars Clock Configuration</h2>
    <p class="msg">{message}</p>

    <form action="/save" method="post" onsubmit="return prepareForm()">
        <input type="hidden" name="client_time" id="client_time">
        <h3>Birthdays</h3>
        <table id="birthdays">
            <tr><th>Name</th><th>Date</th><th></th></tr>
            {birthday_rows}
        </table>
        <button type="button" onclick="addBirthdayRow()">Add Birthday</button>

        <h3>Locations</h3>
        <table id="locations">
            <tr><th>Select</th><th>Name</th><th>Longitude</th><th>Latitude</th><th></th></tr>
            {location_rows}
        </table>
        <button type="button" onclick="addLocationRow()">Add Location</button>

        <br><br>
        <input type="submit" value="Save Settings">
    </form>

    <form action="/done" method="post" onsubmit="return prepareForm()">
        <input type="hidden" name="client_time" id="client_time_done">
        <input type="submit" value="Done – Exit Configuration">
    </form>
</body>
</html>
"""




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
        handle_save(params)
        cfg = load_config()
        response = html_page("Settings saved successfully!", cfg)

    elif "POST /done" in headers:
        params = parse_post_data(body_str)
        handle_done(params)
        response = """<html><body><h2>Configuration Complete</h2>
        <p>The Pico will now shut down. You can disconnect from this Wi-Fi network.</p></body></html>"""

    else:
        cfg = load_config()
        response = html_page("", cfg)

    cl.send('HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n')
    cl.send(response)
    cl.close()



# ---------- SAVE HANDLER ----------

def handle_save(params):
    # Group birthday entries
    birthdays = []
    if "bname" in params and "bdate" in params:
        names = params["bname"]
        dates = params["bdate"]
        # Ensure lists
        if not isinstance(names, list):
            names, dates = [names], [dates]
        for n, d in zip(names, dates):
            if n and d:
                birthdays.append({"name": n, "date": d})

    # Group locations
    locations = []
    if "lname" in params:
        names = params["lname"]
        longs = params.get("longitude", [])
        lats = params.get("latitude", [])
        if not isinstance(names, list):
            names, longs, lats = [names], [longs], [lats]
        for n, lon, lat in zip(names, longs, lats):
            if n:
                locations.append({"name": n, "longitude": lon, "latitude": lat})

    selected = params.get("selectedlocation", "")

    config = {
        "birthdays": birthdays,
        "locations": locations,
        "selectedlocation": selected,
    }

    with open(USER_CONFIG_FILE, "w") as f:
        json.dump(config, f)
    print("Config saved:", config)




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

    

def handle_done(params):
    # Optional: sync RTC from the client
    if "client_time" in params:
        try:
            t = params["client_time"].rstrip("Z")
            date_part, time_part = t.split("T")
            y, m, d = [int(x) for x in date_part.split("-")]
            hh, mm, ss = [int(x) for x in time_part.split(":")]
            rtc = RTC()
            rtc.datetime((y, m, d, 0, hh, mm, ss, 0))
            print("RTC set from browser:", rtc.datetime())
        except Exception as e:
            print("Time set failed:", e)

    print("User finished configuration — shutting down AP...")
    ap = network.WLAN(network.AP_IF)
    ap.active(False)
    machine.reset()


#import network
if __name__ == "__main__":
    ap = network.WLAN(network.AP_IF)

    #network.hostname("picowX")
    ap.config(essid='MarsClockConfig',  password='12345678')
    ap.active(True)
    print('AP IP:', ap.ifconfig()[0])


    # Start mDNS responder
    #mdns_server = mdns.Server()
    #mdns_server.start("ares", "Mars Clock Configuration Server")
    # http://ares.local/

    start_web_server()
    print('Done')

