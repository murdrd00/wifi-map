# WiFi Heatmap Builder

A local, self-contained WiFi signal heatmap tool — like Ekahau or NetSpot, but free and runs entirely on your machine. Upload a floor plan, walk around clicking to record signal strength, and watch a heatmap build in real time.

![Python](https://img.shields.io/badge/python-3.7+-blue) ![No Dependencies](https://img.shields.io/badge/dependencies-none-brightgreen) ![License](https://img.shields.io/badge/license-MIT-green)

## Quick Start

**Windows** — double-click `start.bat`

**Mac / Linux** — double-click `start.sh` (or run `./start.sh`)

Or manually:

```bash
python server.py
```

Open **http://localhost:8199** in your browser. No pip installs, no config, no API keys.

## How It Works

1. **Upload a floor plan** — PNG, JPG, or PDF (multi-page PDFs create one floorplan per page)
2. **Walk to a spot** in your building
3. **Click that spot** on the floor plan — it auto-scans your WiFi and places a measurement point
4. **Repeat** — the more points, the better the heatmap
5. **Export** your data as JSON or PNG

## Features

### Scanning & Measurement
- **One-click scanning** — click the map, get a signal reading instantly
- **Dead zone detection** — if no WiFi is found, automatically marks the spot as a dead zone
- **Manual mode** — use a slider to set dBm values if auto-scan doesn't work on your OS
- **Internet connectivity detection** — shows whether you have internet access at each point
- **Speed testing** — optional download speed test at each measurement point
- **Network list** — see all nearby WiFi networks with signal strength, band, and channel info

### Heatmap Analysis
- **Signal Strength mode** — classic dBm heatmap with customizable color thresholds
- **Signal-to-Noise (SNR) mode** — visualize signal quality relative to noise floor
- **Connectivity mode** — color by internet access and download speed instead of signal strength; instantly spot areas with strong WiFi but no internet (misconfigured APs, captive portals, etc.)
- **Per-SSID filtering** — view the heatmap for a specific network, not just the connected one
- **Band filtering** — filter by 2.4 GHz, 5 GHz, or 6 GHz
- **Independent thresholds** — each heatmap mode has its own color threshold sliders (dBm, dB SNR, Mbps)
- **Internet warning markers** — points with strong signal but no internet get a red warning badge on the map
- **Color legend** — always-visible legend showing the active color scale and filters

### Floor Plans
- **PDF support** — upload PDFs directly; multi-page PDFs create one floorplan per page
- **Multi-floorplan support** — manage multiple floor plans, switch between them freely
- **Background stripping** — remove white or black backgrounds from floor plans for a cleaner overlay
- **Drag & drop upload** — drop an image or PDF directly onto the canvas

### Walls & Perimeter
- **Wall drawing** — draw interior walls as line segments; walls affect how the heatmap blends signal across rooms
- **Wall chaining** — walls automatically chain together for fast drawing
- **Wall material presets** — assign material types (drywall, concrete, metal, etc.) with predefined attenuation values
- **Perimeter tracing** — trace the building perimeter to clip the heatmap to interior spaces
- **Multi-perimeter** — trace multiple separate areas on the same floor plan
- **Snap-to-wall** — new walls snap to existing wall endpoints, wall lines, perimeter vertices, and perimeter edges
- **Wall attenuation** — each wall has a configurable signal attenuation strength

### Access Points
- **AP placement** — mark the physical location of your access points on the floor plan
- **AP naming** — click to rename (e.g. "Main Router", "Office AP")
- **Visual indicators** — APs shown as distinct icons on the map

### Satellite Map Overlay
- **Load by address** — enter any street address to load satellite imagery (Esri World Imagery, no API key needed)
- **Multi-point alignment** — click corresponding points on the satellite map and floor plan to align them. 1 pair = position, 2 pairs = position + rotation + scale, 3+ pairs = full affine correction
- **Opacity control** — adjustable transparency slider
- **Outside only mode** — hides the satellite map inside the building perimeter so it's not distracting
- **Visibility toggle** — show/hide the map entirely

### Tools
- **Scale calibration** — click two points and enter the real-world distance to calibrate measurements
- **Annotations** — place text notes anywhere on the floor plan
- **PNG export** — export the full heatmap as an image with legend, annotations, and scale bar

### Display & Navigation
- **Pan & zoom** — scroll to zoom toward cursor, hold Space to drag, or use the drag mode button
- **Fit to screen** — one-click button to fit the floor plan to your window
- **Light/dark theme** — toggle between light and dark mode
- **Heatmap opacity** — adjustable transparency for the heatmap overlay
- **Toggle points** — show or hide measurement point markers

### Sidebar & Console
- **Collapsible sidebar** — collapse the entire left panel to maximize the map view
- **Collapsible sections** — each sidebar section can be individually collapsed; collapsed sections show summary info (connected network, input mode)
- **Activity console** — timestamped log of every action (points placed, walls drawn, items deleted, etc.)
- **Click-to-undo** — click any console entry to undo that specific action

### Keyboard Shortcuts
| Shortcut | Action |
|----------|--------|
| Space (hold) | Temporary drag/pan mode |
| Ctrl/Cmd + Z | Undo last action (points, walls, perimeter vertices, alignment points) |
| Escape | Cancel current operation (wall chain, alignment, exit mode) |
| Scroll wheel | Zoom toward cursor |

### Data Management
- **Export/Import** — save your heatmap data as JSON, reload later or share with others
- **Auto-save** — data persists in `heatmap_data.json` between sessions
- **Multi-format data** — v2 format supports multiple floorplans with full state per plan
- **100% local** — no data leaves your machine

## Platform Support

| Platform | Auto-Scan Method |
|----------|-----------------|
| macOS | CoreWLAN via `wifi_scan.swift` (primary), `system_profiler` (fallback) |
| Windows | `netsh wlan show interfaces` |
| Linux | `nmcli` / `/proc/net/wireless` / `iwconfig` |

If auto-scan doesn't work on your setup, switch to **Manual mode** and enter signal values yourself.

## Signal Strength Guide

| dBm Range | Quality | Color |
|-----------|---------|-------|
| -30 to -40 | Excellent | Cyan/Blue |
| -40 to -55 | Good | Green |
| -55 to -70 | Fair | Yellow |
| -70 to -85 | Weak | Orange/Red |
| -85 to -100 | Dead zone | Dark Red |

## Tips for Good Heatmaps

- **More points = better accuracy** — aim for 20-30+ points per floor
- **Cover the edges** — especially walls, corners, and transition areas
- **Mark dead spots** — auto-scan handles this, or use manual mode with -95 to -100 dBm
- **Trace walls** — drawing walls lets the heatmap show signal drop-off between rooms
- **Trace the perimeter** — clips the heatmap to your building outline
- **Place your APs** — marking access point locations helps you understand coverage patterns
- **Use the satellite map** — align a satellite view behind your floor plan for spatial context
- **Check connectivity** — switch to Connectivity mode to find areas with signal but no internet

## Project Structure

```
wifi-map/
├── server.py         # Python server — WiFi scanning + static file serving
├── index.html        # Web frontend — entire app in one file
├── wifi_scan.swift   # macOS WiFi scanner (CoreWLAN)
├── start.bat         # Windows launcher (double-click to run)
├── start.sh          # Mac/Linux launcher (double-click to run)
├── LICENSE           # MIT
└── README.md
```

`heatmap_data.json` is created on first use and stores your floor plans, points, walls, perimeters, and settings. It's gitignored since it contains your personal data.

## No Dependencies

Python 3.7+ with zero pip installs. The server uses Python's built-in `http.server` and the frontend is vanilla HTML/CSS/JS. Satellite imagery uses free Esri tiles. PDF support uses [PDF.js](https://mozilla.github.io/pdf.js/) loaded from CDN on first use.

## License

[MIT](LICENSE)
