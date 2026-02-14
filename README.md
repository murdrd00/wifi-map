# WiFi Heatmap Builder

A local, self-contained WiFi signal heatmap tool — like Ekahau or NetSpot, but free and runs entirely on your machine. Upload a floor plan, walk around clicking to record signal strength, and watch a heatmap build in real time.

![Python](https://img.shields.io/badge/python-3.7+-blue) ![No Dependencies](https://img.shields.io/badge/dependencies-none-brightgreen) ![License](https://img.shields.io/badge/license-MIT-green)

## Quick Start

```bash
python server.py
```

Open **http://localhost:8199** in your browser. That's it — no pip installs, no config.

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
- **Point labeling** — click any point name in the sidebar to rename it (e.g. "Kitchen", "Dead zone by elevator")
- **Manual mode** — use a slider to set dBm values if auto-scan doesn't work on your OS
- **IDW interpolation** — Inverse Distance Weighting creates smooth gradients between measurement points
- **Pan & zoom** — scroll to zoom, alt+drag or middle-click to pan, fit-to-screen button
- **Export/Import** — save your heatmap data as JSON, reload later or share with others
- **Auto-save** — data persists in `heatmap_data.json` between sessions
- **Undo** — Ctrl+Z to remove last point (or last wall/floor vertex while drawing)
- **100% local** — no internet needed after first load, no data leaves your machine

## Platform Support

| Platform | Auto-Scan Method |
|----------|-----------------|
| Windows  | `netsh wlan show interfaces` |
| macOS    | `airport -I` |
| Linux    | `nmcli` / `/proc/net/wireless` / `iwconfig` |

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
- **Use wall tracing** — clip the heatmap to your building outline so exterior areas don't get colored
- **Define floors** — if your floor plan has multiple floors on one image, define floor regions to isolate them
- **Stay consistent** — hold your laptop at the same height while scanning

## Project Structure

```
wifi-map/
├── server.py       # Python server — WiFi scanning + static file serving
├── index.html      # Web frontend — entire app in one file
├── LICENSE         # MIT
├── .gitignore
└── README.md
```

`heatmap_data.json` is created on first use and stores your floor plan, points, walls, and floor regions. It's gitignored since it contains your personal data.

## No Dependencies

Python 3.7+ with zero pip installs. The server uses Python's built-in `http.server` and the frontend is vanilla HTML/CSS/JS. PDF support uses [PDF.js](https://mozilla.github.io/pdf.js/) loaded from CDN on first use.

## License

[MIT](LICENSE)
