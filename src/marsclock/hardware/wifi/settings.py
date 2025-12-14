import network, socket #, mdns,
import re, json, machine
from machine import RTC
from marsclock.config import RESOURCE_PATH

SSID = "MarsClockConfig"
PWD = "12345678"

DEFAULT_CONFIG = '/'.join([RESOURCE_PATH, "default_config.json"])
CONFIG_FILE = '/'.join([RESOURCE_PATH, "user_config.json"])

# ---------- CONFIG MANAGEMENT ----------
def load_config():
    try:
        with open(CONFIG_FILE) as fh:
            return json.load(fh)
    except Exception:
        pass
    try:
        with open(DEFAULT_CONFIG) as fh:
            return json.load(fh)
    except Exception:
        return {"birthdays": [], "locations": [], "selectedlocation": ""}

def save_config(cfg):
    with open(CONFIG_FILE, "w") as f:
        json.dump(cfg, f)


class SettingsApServer:
    def __init__(self):
        self.addr = None
        self.ap = None
        self.ssid = SSID
        self.pwd = PWD
        self.start_ap()

    # ---------- AP & SERVER ----------
    def start(self):
        ap = network.WLAN(network.AP_IF)
        ap.config(essid=self.ssid, password=self.pwd)
        ap.active(True)
        while not ap.active():
            pass
        print("AP active, connect to:", ap.ifconfig())
        self.ap = ap

        # --------- Open Socket
        addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
        s = socket.socket()
        s.bind(addr)
        s.listen(1)
        print('Listening on', addr)
        self.addr = addr
        self.s = s


    def listen(self):
        while True:
            client, addr = self.s.accept()
            self.handle_client(client)


    def shutdown_web_server(self):
        print("User finished configuration — shutting down AP...")
        ap = network.WLAN(network.AP_IF)
        ap.active(False)
        machine.reset()


    def handle_client(self, client):
        session_complete = False
        try:
            headers, body_str = parse_request(client)

            if "POST /save" in headers:
                params = parse_post_data(body_str)
                self.handle_save(params)
                response = html_page("Settings saved successfully!", load_config())

            elif "POST /done" in headers:
                params = parse_post_data(body_str)
                handle_done(params)
                session_complete = True
                response = """<html><body><h2>Configuration Complete</h2>
                <p>The Pico will now shut down. You may disconnect.</p></body></html>"""

            else:
                response = html_page("", load_config())

            client.send("HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n")
            client.send(response)
        except Exception as e:
            print("Error:", e)
        finally:
            client.close()
        if session_complete:
            self.shutdown_web_server()


    # ---------- SAVE HANDLER ----------
    def handle_save(self, params):
        cfg = {"birthdays": [], "locations": [], "selectedlocation": ""}
        if "b_name" in params and "b_date" in params:
            for name, date in zip(params.get("b_name", []), params.get("b_date", [])):
                if name.strip():
                    cfg["birthdays"].append({"name": name.strip(), "date": date.strip()})
        if "l_name" in params:
            for n, lo, la in zip(params.get("l_name", []), params.get("l_long", []), params.get("l_lat", [])):
                if n.strip():
                    cfg["locations"].append({
                        "name": n.strip(),
                        "longitude": lo.strip(),
                        "latitude": la.strip()
                    })
        if "selectedlocation" in params:
            cfg["selectedlocation"] = params["selectedlocation"][0]
        else:
            cfg["selectedlocation"] = cfg["locations"][0]['name']

        save_config(cfg)

        # Update RTC from client UTC time
        #if "client_time" in params:
        #    set_rtc_from_client(params["client_time"][0])
         
        #print("Configuration saved:", cfg)


    
def parse_request(client):
    req = b""
    while True:
        chunk = client.recv(1024)
        if not chunk: break
        req += chunk
        if b"\r\n\r\n" in req:
            if b"Content-Length" in req:
                header_end = req.find(b"\r\n\r\n") + 4
                headers = req[:header_end].decode()
                content_length = 0
                for line in headers.split("\r\n"):
                    if line.lower().startswith("content-length:"):
                        content_length = int(line.split(":")[1])
                body = req[header_end:]
                while len(body) < content_length:
                    body += client.recv(1024)
                full = headers.encode() + body
                req = full
            break

    request_str = req.decode()
    header_end = request_str.find("\r\n\r\n")
    headers = request_str[:header_end]
    body_str = request_str[header_end+4:]
    return headers, body_str


def parse_post_data(body):
    params = {}
    for pair in body.split("&"):
        if "=" in pair:
            k, v = pair.split("=", 1)
            k = re.sub("%([0-9A-Fa-f]{2})", lambda m: chr(int(m.group(1), 16)), k)
            v = re.sub("%([0-9A-Fa-f]{2})", lambda m: chr(int(m.group(1), 16)), v)
            params.setdefault(k, []).append(v.replace("+", " "))
    return params


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


