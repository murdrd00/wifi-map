# WiFi Heatmap Builder

A local, self-contained WiFi signal heatmap tool — like NetSpot, but free and runs entirely on your machine. Upload a floor plan, walk around clicking to record signal strength, and watch a heatmap build in real time.

![Runs Locally](https://img.shields.io/badge/runs-locally-green) ![Python](https://img.shields.io/badge/python-3.7+-blue) ![No Dependencies](https://img.shields.io/badge/dependencies-none-brightgreen)

## Quick Start

```bash
cd wifi-map
python server.py
```

Open **http://localhost:8199** in your browser. No pip installs needed.

## How It Works

1. **Upload a floor plan** — PNG, JPG, or PDF (any image works: photo, screenshot, CAD export, hand-drawn sketch)
2. **Walk to a spot** in your building
3. **Click that spot** on the floor plan — it auto-scans your WiFi signal strength and places a point
4. **Repeat** — the more points, the better the heatmap
5. **Export** your data as JSON to save or share

## Features

- **One-click scanning** — click the map, get a signal reading, done
- **Dead zone detection** — if no WiFi is found, automatically marks the spot as a dead zone
- **PDF floor plans** — upload PDFs directly, first page is rendered as your map
- **Wall tracing** — trace your building perimeter to clip the heatmap to interior spaces only
- **Multi-floor support** — define floor regions so points on one floor don't bleed into another
- **Point renaming** — click any point name in the sidebar to label it (e.g. "Kitchen", "Dead zone by elevator")
- **Manual mode** — use a slider to set dBm values if auto-scan doesn't work on your OS
- **IDW interpolation** — Inverse Distance Weighting creates smooth gradients between measurement points
- **Pan & zoom** — scroll to zoom, alt+drag or middle-click to pan, fit-to-screen button
- **Export/Import** — save your heatmap data as JSON, reload later or share with others
- **Auto-save** — data persists in `heatmap_data.json` between sessions
- **Undo** — Ctrl+Z to remove last point (or last wall/floor vertex while drawing)
- **Runs 100% locally** — no internet needed after first load, no data leaves your machine

## Platform Support

| Platform | Auto-Scan Method |
|----------|-----------------|
| Windows  | `netsh wlan show interfaces` |
| macOS    | `airport -I` command |
| Linux    | `nmcli`, `/proc/net/wireless`, or `iwconfig` |

If auto-scan doesn't work, switch to **Manual mode** and enter signal strength values from another WiFi analyzer app.

## Signal Strength Guide

| dBm Range | Quality | Color |
|-----------|---------|-------|
| -30 to -40 | Excellent | Cyan/Blue |
| -40 to -55 | Good | Green |
| -55 to -70 | Fair | Yellow |
| -70 to -85 | Weak | Orange/Red |
| -85 to -100 | Dead zone | Dark Red |

## Tips for Good Heatmaps

- **More points = better accuracy** — aim for 20–30+ points per floor
- **Cover the edges** — especially walls, corners, and transition areas
- **Mark dead spots** — auto-scan handles this, or use manual mode with -95 to -100 dBm
- **Use wall tracing** — clip the heatmap to your building outline so exterior areas don't get colored
- **Define floors** — if your floor plan has multiple floors on one image, define floor regions to isolate them
- **Consistency** — try to hold your laptop at a consistent height while scanning

## Files

```
wifi-map/
├── server.py          # Python server (WiFi scanning + static file serving)
├── index.html         # Web frontend (entire app in one file)
├── .gitignore         # Ignores auto-saved data
└── README.md
```

`heatmap_data.json` is created automatically on first use and contains your saved floor plan, points, walls, and floor regions. It's gitignored since it contains your personal data.

## No Dependencies

Runs on Python 3.7+ with zero pip installs. The server uses Python's built-in `http.server` and the frontend is vanilla HTML/CSS/JS. PDF support uses [PDF.js](https://mozilla.github.io/pdf.js/) loaded from CDN on first use.
