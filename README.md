# PolyTile

**PolyTile** is a lightweight Python desktop application built with **PyQt6** and **OpenCV** that automates the creation of 2D polygon collision shapes for spritesheets and tilesets. 

By analyzing the alpha (transparency) channel of your PNG images, PolyTile automatically detects the contour of each tile, simplifies it into a polygon, and exports the data to a clean JSON structure ready to be used in game engines (such as Godot, Unity, Defold, or custom engines).

---

## Features

- 🔍 **Interactive Viewer:** Zoom with the mouse wheel and pan with the right mouse button to easily inspect large tilesets.
- 📐 **Grid Segmentation:** Define custom tile widths and heights (e.g., 16x16, 32x32, 64x64) to fit your assets.
- ⚙️ **Contour Approximation:** Fine-tune the transparency (alpha) threshold to detect even faint or semi-transparent outlines.
- 🎨 **Visual Feedback:** Real-time overlay showing grid cells and the generated collision polygons.
- 💾 **JSON Export:** Exports a structured JSON file containing grid locations, frame IDs, and relative polygon coordinates (`[x, y]` points).
- 🚀 **Executable Packaging:** Includes a PyInstaller spec file to easily build a standalone executable.

---

## Installation

### Prerequisites
Make sure you have Python 3.8+ installed.

### Setup
1. Clone this repository:
   ```bash
   git clone https://github.com/markuskahl/PolyTile.git
   cd PolyTile
   ```

2. Install the required dependencies:
   ```bash
   pip install PyQt6 opencv-python numpy
   ```

---

## Usage

1. **Run the App:**
   ```bash
   python app.py
   ```
2. **Load a Tileset:** Click on **1. Tileset laden** and select a PNG image with transparency.
3. **Configure Grid & Threshold:**
   - Adjust **Breite** (Width) and **Höhe** (Height) in pixels to match your tiles.
   - Adjust the **Alpha-Limit** threshold (0 to 255) for contour detection.
4. **Generate Polygons:** Click on **2. Polygone generieren** to compute and preview the collision outlines (shown in green).
5. **Export to JSON:** Click on **3. Als JSON exportieren** to save the collision data.

---

## Export Format (JSON)

The exported JSON structure looks like this:

```json
{
    "tileset_name": "my_tileset.png",
    "tile_size": {
        "width": 32,
        "height": 32
    },
    "frames": [
        {
            "frame_id": 0,
            "grid_position": {
                "row": 0,
                "col": 0
            },
            "polygon": [
                [0, 16],
                [16, 0],
                [32, 16],
                [16, 32]
            ]
        }
    ]
}
```

---

## Building a Standalone Executable

You can package PolyTile into a single, standalone executable file using PyInstaller:

1. Install PyInstaller:
   ```bash
   pip install pyinstaller
   ```
2. Build the app:
   ```bash
   pyinstaller app.spec
   ```
3. Find your executable in the `dist/` directory!

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
