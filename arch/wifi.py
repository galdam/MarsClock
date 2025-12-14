import network, socket #, mdns,
import re, json, machine
from machine import RTC

CONFIG_FILE = "user_config.json"

# ---------- CONFIG MANAGEMENT ----------
def load_config():
    try:
        with open(CONFIG_FILE) as fh:
            return json.load(fh)
    except Exception:
        return {"birthdays": [], "locations": [], "selectedlocation": ""}

def save_config(cfg):
    with open(CONFIG_FILE, "w") as f:
        json.dump(cfg, f)

# ---------- HTML PAGE ----------
def html_page(message="", cfg=None):
    if cfg is None:
        cfg = load_config()

    birthdays_html = ""
    for b in cfg.get("birthdays", []):
        birthdays_html += f'''
        <div class="birthday">
            <input name="b_name" value="{b['name']}" placeholder="Name">
            <input name="b_date" value="{b['date']}" placeholder="YYYY-MM-DD">
            <button type="button" onclick="this.parentElement.remove()">Remove</button>
        </div>'''

    locations_html = ""
    selected = cfg.get("selectedlocation", "")
    for loc in cfg.get("locations", []):
        checked = "checked" if loc["name"] == selected else ""
        locations_html += f'''
        <div class="location">
            <input name="l_name" value="{loc['name']}" placeholder="Name">
            <input name="l_long" value="{loc['longitude']}" placeholder="Longitude">
            <input name="l_lat" value="{loc['latitude']}" placeholder="Latitude">
            <input type="radio" name="selectedlocation" value="{loc['name']}" {checked}>
            <button type="button" onclick="this.parentElement.remove()">Remove</button>
        </div>'''

    return f"""<!DOCTYPE html>
<html>
<head>
<title>Pico Configuration</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
body {{ font-family: sans-serif; margin: 20px; }}
section {{ border:1px solid #ccc; padding:10px; border-radius:8px; margin-bottom:20px; }}
input,button {{ margin:4px; }}
</style>
<script>
function addBirthday() {{
    const div = document.createElement('div');
    div.className = 'birthday';
    div.innerHTML = '<input name="b_name" placeholder="Name"> <input name="b_date" placeholder="YYYY-MM-DD"> <button type="button" onclick="this.parentElement.remove()">Remove</button>';
    document.getElementById('birthdays').appendChild(div);
}}
function addLocation() {{
    const div = document.createElement('div');
    div.className = 'location';
    div.innerHTML = '<input name="l_name" placeholder="Name"> <input name="l_long" placeholder="Longitude"> <input name="l_lat" placeholder="Latitude"> <input type="radio" name="selectedlocation"> <button type="button" onclick="this.parentElement.remove()">Remove</button>';
    document.getElementById('locations').appendChild(div);
}}
function setClientUTCTime() {{
    const now = new Date();
    const formatted = now.getUTCFullYear() + '-' +
        String(now.getUTCMonth()+1).padStart(2, '0') + '-' +
        String(now.getUTCDate()).padStart(2, '0') + 'T' +
        String(now.getUTCHours()).padStart(2, '0') + ':' +
        String(now.getUTCMinutes()).padStart(2, '0') + ':' +
        String(now.getUTCSeconds()).padStart(2, '0') + 'Z';
    document.querySelectorAll("input[id^='client_time']").forEach(f => f.value = formatted);
}}
function prepareForm() {{
    setClientUTCTime();
    return true;
}}
</script>
</head>
<body>
<h2>Pico Configuration</h2>
<p style="color:green;">{message}</p>

<form action="/save" method="post" onsubmit="return prepareForm()">
  <input type="hidden" id="client_time" name="client_time">
  
  <section>
    <h3>Birthdays</h3>
    <div id="birthdays">{birthdays_html}</div>
    <button type="button" onclick="addBirthday()">Add Birthday</button>
  </section>

  <section>
    <h3>Locations</h3>
    <div id="locations">{locations_html}</div>
    <button type="button" onclick="addLocation()">Add Location</button>
  </section>

  <input type="submit" value="Save Settings">
</form>

<form action="/done" method="post" onsubmit="return prepareForm()">
  <input type="hidden" id="client_time_done" name="client_time">
  <input type="submit" value="Done – Exit Configuration">
</form>

</body>
</html>"""

# ---------- UTILITY ----------
def parse_post_data(body):
    params = {}
    for pair in body.split("&"):
        if "=" in pair:
            k, v = pair.split("=", 1)
            k = re.sub("%([0-9A-Fa-f]{2})", lambda m: chr(int(m.group(1), 16)), k)
            v = re.sub("%([0-9A-Fa-f]{2})", lambda m: chr(int(m.group(1), 16)), v)
            params.setdefault(k, []).append(v.replace("+", " "))
    return params

# ---------- SAVE HANDLER ----------
def handle_save(params):
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
    if "client_time" in params:
        set_rtc_from_client(params["client_time"][0])
    print("Configuration saved:", cfg)

def handle_done(params):
    if "client_time" in params:
        set_rtc_from_client(params["client_time"][0])

def set_rtc_from_client(timestr):
    try:
        t = timestr.rstrip("Z")
        date_part, time_part = t.split("T")
        y, m, d = [int(x) for x in date_part.split("-")]
        hh, mm, ss = [int(x) for x in time_part.split(":")]
        rtc = RTC()
        rtc.datetime((y, m, d, 0, hh, mm, ss, 0))
        print("RTC set (UTC):", rtc.datetime())
    except Exception as e:
        print("Failed to parse client time:", e)

# ---------- AP & SERVER ----------
def start_ap():
    ap = network.WLAN(network.AP_IF)
    ap.config(essid="MarsClockConfig", password="12345678")
    ap.active(True)
    while not ap.active():
        pass
    print("AP active, connect to:", ap.ifconfig())

    # Start mDNS responder
    #mdns_server = mdns.Server()
    #mdns_server.start("ares", "Mars Clock Configuration Server")
    # http://ares.local/
    return ap, None #mdns_server

def start_web_server():
    addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
    s = socket.socket()
    s.bind(addr)
    s.listen(1)
    print('Listening on', addr)
    while True:
        cl, addr = s.accept()
        handle_client(cl)


def shutdown_web_server():
    print("User finished configuration — shutting down AP...")
    ap = network.WLAN(network.AP_IF)
    ap.active(False)
    machine.reset()


def parse_request(cl):
    req = b""
    while True:
        chunk = cl.recv(1024)
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
                    body += cl.recv(1024)
                full = headers.encode() + body
                req = full
            break

    request_str = req.decode()
    header_end = request_str.find("\r\n\r\n")
    headers = request_str[:header_end]
    body_str = request_str[header_end+4:]
    return headers, body_str


def handle_client(cl):
    session_complete = False
    try:
        headers, body_str = parse_request(cl)

        if "POST /save" in headers:
            params = parse_post_data(body_str)
            handle_save(params)
            response = html_page("Settings saved successfully!", load_config())

        elif "POST /done" in headers:
            params = parse_post_data(body_str)
            handle_done(params)
            session_complete = True
            response = """<html><body><h2>Configuration Complete</h2>
            <p>The Pico will now shut down. You may disconnect.</p></body></html>"""

        else:
            response = html_page("", load_config())

        cl.send("HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n")
        cl.send(response)
    except Exception as e:
        print("Error:", e)
    finally:
        cl.close()
    if session_complete:
        shutdown_web_server()

# ---------- MAIN ----------
if __name__ == "__main__":
    ap, mdns_server = start_ap()
    start_web_server()
