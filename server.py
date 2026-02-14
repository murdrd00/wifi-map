#!/usr/bin/env python3
"""
WiFi Heatmap Builder — Local server
Run this, open the browser, upload your floor plan, and walk around clicking to record signal strength.
"""

import http.server
import json
import subprocess
import platform
import re
import os
import sys

import socketserver

PORT = 8199
DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "heatmap_data.json")


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SWIFT_SCANNER = os.path.join(SCRIPT_DIR, "wifi_scan.swift")


def _scan_darwin(result):
    """Scan WiFi on macOS using CoreWLAN (via Swift helper) with system_profiler fallback."""
    # Primary: Swift CoreWLAN scanner — gets SSIDs and all nearby networks
    if os.path.exists(SWIFT_SCANNER):
        try:
            out = subprocess.check_output(
                ["swift", SWIFT_SCANNER], stderr=subprocess.DEVNULL, timeout=15
            ).decode()
            data = json.loads(out)
            result["signal_dbm"] = data.get("rssi")
            result["noise_dbm"] = data.get("noise")
            result["channel"] = str(data["channel"]) if data.get("channel") else None
            result["band"] = data.get("band")
            result["ssid"] = data.get("ssid")
            tx = data.get("tx_rate")
            if tx:
                result["link_speed"] = f"{tx} Mbps"
            if result["signal_dbm"] is not None:
                result["signal_percent"] = max(0, min(100, 2 * (result["signal_dbm"] + 100)))
            # Include nearby networks
            networks = data.get("networks", [])
            if networks:
                result["nearby_networks"] = []
                for n in networks:
                    ssid = n.get("ssid", "")
                    if not ssid:
                        continue  # Skip hidden networks
                    dbm = n.get("rssi", -100)
                    result["nearby_networks"].append({
                        "ssid": ssid,
                        "signal_dbm": dbm,
                        "signal_percent": max(0, min(100, 2 * (dbm + 100))),
                        "noise_dbm": n.get("noise"),
                        "channel": n.get("channel"),
                        "band": n.get("band"),
                        "is_connected": n.get("is_connected", False),
                    })
            return
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, json.JSONDecodeError, KeyError):
            pass  # Fall through to system_profiler

    # Fallback: airport command (macOS < Sonoma)
    airport = "/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport"
    if os.path.exists(airport):
        out = subprocess.check_output([airport, "-I"], stderr=subprocess.DEVNULL, timeout=5).decode()
        for line in out.strip().split("\n"):
            line = line.strip()
            if line.startswith("SSID:"):
                result["ssid"] = line.split(":", 1)[1].strip()
            elif line.startswith("agrCtlRSSI:"):
                dbm = int(line.split(":", 1)[1].strip())
                result["signal_dbm"] = dbm
                result["signal_percent"] = max(0, min(100, 2 * (dbm + 100)))
            elif line.startswith("agrCtlNoise:"):
                result["noise_dbm"] = int(line.split(":", 1)[1].strip())
            elif line.startswith("channel:"):
                result["channel"] = line.split(":", 1)[1].strip()
            elif line.startswith("lastTxRate:"):
                result["link_speed"] = line.split(":", 1)[1].strip() + " Mbps"
        return

    # Fallback: system_profiler (macOS Sonoma+ without Swift)
    out = subprocess.check_output(
        ["system_profiler", "SPAirPortDataType"], stderr=subprocess.DEVNULL, timeout=10
    ).decode()
    in_current_network = False
    for line in out.split("\n"):
        stripped = line.strip()
        if "Current Network Information:" in stripped:
            in_current_network = True
            continue
        if "Other Local Wi-Fi Networks:" in stripped:
            break
        if not in_current_network:
            continue
        if "Signal / Noise:" in stripped:
            m = re.search(r"(-?\d+)\s*dBm\s*/\s*(-?\d+)\s*dBm", stripped)
            if m:
                dbm = int(m.group(1))
                result["signal_dbm"] = dbm
                result["signal_percent"] = max(0, min(100, 2 * (dbm + 100)))
                result["noise_dbm"] = int(m.group(2))
        elif "Channel:" in stripped:
            m = re.search(r"Channel:\s*(\S+)", stripped)
            if m:
                result["channel"] = m.group(1)
        elif "Transmit Rate:" in stripped:
            m = re.search(r"Transmit Rate:\s*(\S+)", stripped)
            if m:
                result["link_speed"] = m.group(1) + " Mbps"


def get_wifi_info():
    """Get current WiFi signal strength and network info. Works on macOS, Linux, Windows."""
    system = platform.system()
    result = {
        "ssid": None,
        "signal_dbm": None,      # dBm (negative number, closer to 0 = better)
        "signal_percent": None,   # 0-100%
        "frequency": None,
        "band": None,            # "2.4 GHz", "5 GHz", or "6 GHz"
        "channel": None,
        "link_speed": None,
        "noise_dbm": None,       # Noise floor in dBm (macOS)
        "nearby_networks": None,  # List of all visible networks
        "error": None,
    }

    try:
        if system == "Darwin":  # macOS
            _scan_darwin(result)

        elif system == "Linux":
            # Try nmcli first (most common on modern distros)
            try:
                out = subprocess.check_output(
                    ["nmcli", "-t", "-f", "ACTIVE,SSID,SIGNAL,FREQ,CHAN,RATE", "dev", "wifi"],
                    stderr=subprocess.DEVNULL, timeout=5
                ).decode()
                for line in out.strip().split("\n"):
                    parts = line.split(":")
                    if parts[0] == "yes":
                        result["ssid"] = parts[1] if len(parts) > 1 else None
                        if len(parts) > 2 and parts[2]:
                            pct = int(parts[2])
                            result["signal_percent"] = pct
                            # Approximate dBm from percentage
                            result["signal_dbm"] = int(pct / 2 - 100)
                        result["frequency"] = parts[3] if len(parts) > 3 else None
                        result["channel"] = parts[4] if len(parts) > 4 else None
                        result["link_speed"] = parts[5] if len(parts) > 5 else None
                        break
            except (FileNotFoundError, subprocess.CalledProcessError):
                pass

            # Fallback: /proc/net/wireless
            if result["signal_dbm"] is None:
                try:
                    with open("/proc/net/wireless") as f:
                        lines = f.readlines()
                    for line in lines[2:]:  # skip header
                        parts = line.split()
                        if len(parts) >= 4:
                            iface = parts[0].rstrip(":")
                            # Quality and signal level
                            signal = float(parts[3].rstrip("."))
                            if signal < 0:
                                result["signal_dbm"] = int(signal)
                            else:
                                result["signal_dbm"] = int(signal - 256) if signal > 63 else int(signal)
                            result["signal_percent"] = max(0, min(100, 2 * (result["signal_dbm"] + 100)))
                            break
                except (FileNotFoundError, PermissionError):
                    pass

            # Fallback: iwconfig
            if result["signal_dbm"] is None:
                try:
                    out = subprocess.check_output(
                        ["iwconfig"], stderr=subprocess.DEVNULL, timeout=5
                    ).decode()
                    m = re.search(r'ESSID:"([^"]*)"', out)
                    if m:
                        result["ssid"] = m.group(1)
                    m = re.search(r"Signal level=(-?\d+)", out)
                    if m:
                        dbm = int(m.group(1))
                        result["signal_dbm"] = dbm
                        result["signal_percent"] = max(0, min(100, 2 * (dbm + 100)))
                    m = re.search(r"Bit Rate=(\S+)", out)
                    if m:
                        result["link_speed"] = m.group(1)
                except (FileNotFoundError, subprocess.CalledProcessError):
                    pass

        elif system == "Windows":
            out = subprocess.check_output(
                ["netsh", "wlan", "show", "interfaces"], stderr=subprocess.DEVNULL, timeout=5
            ).decode()
            for line in out.strip().split("\n"):
                line = line.strip()
                if line.startswith("SSID") and "BSSID" not in line:
                    result["ssid"] = line.split(":", 1)[1].strip()
                elif line.startswith("Signal"):
                    pct_str = line.split(":", 1)[1].strip().rstrip("%")
                    pct = int(pct_str)
                    result["signal_percent"] = pct
                    result["signal_dbm"] = int(pct / 2 - 100)
                elif line.startswith("Channel"):
                    result["channel"] = line.split(":", 1)[1].strip()
                elif "Receive rate" in line or "Transmit rate" in line:
                    result["link_speed"] = line.split(":", 1)[1].strip()
                elif "Radio type" in line or "Band" in line:
                    result["frequency"] = line.split(":", 1)[1].strip()

    except subprocess.TimeoutExpired:
        result["error"] = "WiFi scan timed out"
    except Exception as e:
        result["error"] = str(e)

    # Derive band from channel number if not already set
    if result["band"] is None and result["channel"]:
        try:
            # Channel string might be "36" or "36,+1" (macOS bonded channels)
            ch = int(re.split(r'[^0-9]', str(result["channel"]))[0])
            if 1 <= ch <= 14:
                result["band"] = "2.4 GHz"
            elif 32 <= ch <= 177:
                result["band"] = "5 GHz"
            elif ch >= 1 and result.get("frequency") and "6" in str(result["frequency"]):
                result["band"] = "6 GHz"
        except (ValueError, IndexError):
            pass

    # Derive band from frequency string (Windows "Radio type" or "Band" field)
    if result["band"] is None and result["frequency"]:
        freq = str(result["frequency"]).lower()
        if "2.4" in freq:
            result["band"] = "2.4 GHz"
        elif "5" in freq and "6" not in freq:
            result["band"] = "5 GHz"
        elif "6" in freq:
            result["band"] = "6 GHz"

    # If we got nothing at all
    if result["signal_dbm"] is None and result["signal_percent"] is None and not result["error"]:
        result["error"] = f"Could not read WiFi signal on {system}. Make sure WiFi is connected."

    # Quick internet connectivity check (non-blocking, best-effort)
    result["has_internet"] = _check_internet()

    return result


def _check_internet():
    """Quick check if we can reach the internet. Returns True/False/None."""
    import urllib.request
    try:
        urllib.request.urlopen("http://captive.apple.com/hotspot-detect.html", timeout=3)
        return True
    except Exception:
        return False


def load_data():
    """Load saved heatmap data from disk."""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"points": [], "floorplan": None, "walls": []}


def save_data(data):
    """Persist heatmap data to disk."""
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


class HeatmapHandler(http.server.SimpleHTTPRequestHandler):
    """Handle API requests and serve the frontend."""

    def do_GET(self):
        if self.path == "/":
            self.path = "/index.html"
            # Serve from script directory
            filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "index.html")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            with open(filepath, "rb") as f:
                self.wfile.write(f.read())
            return

        elif self.path == "/api/scan":
            info = get_wifi_info()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(info).encode())
            return

        elif self.path == "/api/data":
            data = load_data()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(data).encode())
            return

        super().do_GET()

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)

        if self.path == "/api/data":
            data = json.loads(body)
            save_data(data)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"ok": True}).encode())
            return

        elif self.path == "/api/scan-and-add":
            # Scan wifi and return the result — client handles adding to map
            info = get_wifi_info()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(info).encode())
            return

        self.send_response(404)
        self.end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def log_message(self, format, *args):
        # Quieter logging
        if "/api/" in str(args[0]):
            return
        super().log_message(format, *args)


def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # Quick initial scan to verify WiFi works
    print("=" * 60)
    print("  WiFi Heatmap Builder")
    print("=" * 60)
    print(f"\n  Testing WiFi scan on {platform.system()}...")
    info = get_wifi_info()
    if info["error"]:
        print(f"  [!] Warning: {info['error']}")
        print("  You can still use manual signal entry mode.\n")
    else:
        print(f"  [+] Connected to: {info['ssid']}")
        print(f"  [+] Signal: {info['signal_dbm']} dBm ({info['signal_percent']}%)\n")

    with socketserver.TCPServer(("", PORT), HeatmapHandler) as httpd:
        print(f"  Open http://localhost:{PORT} in your browser")
        print(f"  Press Ctrl+C to stop\n")
        print("=" * 60)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down.")
            httpd.shutdown()


if __name__ == "__main__":
    main()
