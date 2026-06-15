import sys
import os
import json
import cv2
import numpy as np
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QSpinBox, 
                             QFileDialog, QGraphicsScene, QGraphicsView, QMessageBox)
from PyQt6.QtGui import QPixmap, QImage, QPen, QColor
from PyQt6.QtCore import Qt

class ZoomableGraphicsView(QGraphicsView):
    """ Eine angepasste QGraphicsView, die Zoom und Panning unterstützt """
    def __init__(self, scene):
        super().__init__(scene)
        # Die fehlerhafte QImage-Zeile wurde hier restlos entfernt!
        
        # Erlaubt das Verschieben des Bildes mit der Hand (Mausrad gedrückt halten / rechte Maustaste)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)

    def wheelEvent(self, event):
        """ Fängt das Mausrad ab, um pixelgenau zu zoomen """
        zoom_factor = 1.15
        if event.angleDelta().y() > 0:
            self.scale(zoom_factor, zoom_factor)
        else:
            self.scale(1.0 / zoom_factor, 1.0 / zoom_factor)

    def mousePressEvent(self, event):
        """ Erlaubt Panning mit rechter Maustaste, blockiert nicht das normale Klicken """
        if event.button() == Qt.MouseButton.RightButton:
            release_event = event.__class__(event.type(), event.position(), event.globalPosition(),
                                            Qt.MouseButton.LeftButton, event.buttons() | Qt.MouseButton.LeftButton,
                                            event.modifiers())
            super().mousePressEvent(release_event)
        else:
            super().mousePressEvent(event)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PolyTile")
        self.setGeometry(100, 100, 1024, 768)

        # Status-Variablen
        self.image_path = None
        self.cv_img = None
        self.polygon_data = None

        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout()

        # --- LINKE SEITE: KONTROLL-PANEL ---
        control_panel = QVBoxLayout()
        control_panel.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        self.btn_load = QPushButton("1. Tileset laden")
        self.btn_load.clicked.connect(self.load_image)
        control_panel.addWidget(self.btn_load)
        
        control_panel.addWidget(QLabel("\nGrid-Einstellungen (Pixel):"))
        
        hbox_w = QHBoxLayout()
        hbox_w.addWidget(QLabel("Breite:"))
        self.spin_width = QSpinBox()
        self.spin_width.setRange(4, 512)
        self.spin_width.setValue(32)
        self.spin_width.valueChanged.connect(self.draw_grid_and_preview)
        hbox_w.addWidget(self.spin_width)
        control_panel.addLayout(hbox_w)

        hbox_h = QHBoxLayout()
        hbox_h.addWidget(QLabel("Höhe:"))
        self.spin_height = QSpinBox()
        self.spin_height.setRange(4, 512)
        self.spin_height.setValue(32)
        self.spin_height.valueChanged.connect(self.draw_grid_and_preview)
        hbox_h.addWidget(self.spin_height)
        control_panel.addLayout(hbox_h)

        control_panel.addWidget(QLabel("\nAlgorithmus-Feinjustierung:"))
        
        hbox_t = QHBoxLayout()
        hbox_t.addWidget(QLabel("Alpha-Limit (0-255):"))
        self.spin_thresh = QSpinBox()
        self.spin_thresh.setRange(0, 255)
        self.spin_thresh.setValue(10)
        hbox_t.addWidget(self.spin_thresh)
        control_panel.addLayout(hbox_t)

        self.btn_generate = QPushButton("2. Polygone generieren")
        self.btn_generate.setStyleSheet("background-color: #2b579a; color: white; font-weight: bold;")
        self.btn_generate.clicked.connect(self.generate_polygons)
        self.btn_generate.setEnabled(False)
        control_panel.addWidget(self.btn_generate)

        self.btn_export = QPushButton("3. Als JSON exportieren")
        self.btn_export.setStyleSheet("background-color: #1e7145; color: white; font-weight: bold;")
        self.btn_export.clicked.connect(self.export_to_json)
        self.btn_export.setEnabled(False)
        control_panel.addWidget(self.btn_export)

        control_panel.addWidget(QLabel("\nSteuerung im Viewer:"))
        control_panel.addWidget(QLabel("• Mausrad: Zoom In/Out\n• Rechte Maus halten: Bild verschieben"))

        self.lbl_info = QLabel("\nBitte ein Bild laden...")
        self.lbl_info.setWordWrap(True)
        control_panel.addWidget(self.lbl_info)

        # --- RECHTE SEITE: GRAFIK-ANSICHT ---
        self.scene = QGraphicsScene()
        self.view = ZoomableGraphicsView(self.scene)

        # Zusammenfügen
        control_widget = QWidget()
        control_widget.setLayout(control_panel)
        control_widget.setFixedWidth(220)

        main_layout.addWidget(control_widget)
        main_layout.addWidget(self.view)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def load_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Tileset öffnen", "", "Bilder (*.png)")
        if not file_path:
            return

        self.image_path = file_path
        self.cv_img = cv2.imread(file_path, cv2.IMREAD_UNCHANGED)

        if self.cv_img is None or self.cv_img.shape[2] < 4:
            QMessageBox.critical(self, "Fehler", "Das Bild konnte nicht geladen werden oder besitzt keinen Alpha-Kanal (Transparenz)!")
            return

        self.btn_generate.setEnabled(True)
        self.btn_export.setEnabled(False)
        self.polygon_data = None
        
        self.view.resetTransform()
        self.draw_grid_and_preview()

    def draw_grid_and_preview(self):
        if self.cv_img is None:
            return

        self.scene.clear()

        height, width, channels = self.cv_img.shape
        bytes_per_line = channels * width
        rgb_img = cv2.cvtColor(self.cv_img, cv2.COLOR_BGRA2RGBA)
        q_img = QImage(rgb_img.data, width, height, bytes_per_line, QImage.Format.Format_RGBA8888)
        pixmap = QPixmap.fromImage(q_img)

        self.scene.addPixmap(pixmap)
        self.scene.setSceneRect(0, 0, width, height)

        tile_w = self.spin_width.value()
        tile_h = self.spin_height.value()
        
        grid_pen = QPen(QColor(255, 0, 0, 100))
        grid_pen.setWidth(1)
        grid_pen.setStyle(Qt.PenStyle.DashLine)

        for x in range(0, width, tile_w):
            self.scene.addLine(x, 0, x, height, grid_pen)
        for y in range(0, height, tile_h):
            self.scene.addLine(0, y, width, y, grid_pen)

        self.lbl_info.setText(f"Bild geladen: {width}x{height}px\nRaster: {width//tile_w}x{height//tile_h} Frames.")

    def generate_polygons(self):
        if self.cv_img is None:
            return

        self.draw_grid_and_preview()

        tile_width = self.spin_width.value()
        tile_height = self.spin_height.value()
        alpha_thresh = self.spin_thresh.value()

        img_height, img_width, _ = self.cv_img.shape
        cols = img_width // tile_width
        rows = img_height // tile_height

        self.polygon_data = {
            "tileset_name": os.path.basename(self.image_path),
            "tile_size": {"width": tile_width, "height": tile_height},
            "frames": []
        }

        polygon_pen = QPen(QColor(0, 255, 0, 255))
        polygon_pen.setWidth(2)

        frame_counter = 0
        detected_count = 0

        for r in range(rows):
            for c in range(cols):
                start_x = c * tile_width
                start_y = r * tile_height

                frame = self.cv_img[start_y:start_y+tile_height, start_x:start_x+tile_width]
                alpha_channel = frame[:, :, 3]

                _, thresh = cv2.threshold(alpha_channel, alpha_thresh, 255, cv2.THRESH_BINARY)
                contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                if contours:
                    largest_contour = max(contours, key=cv2.contourArea)
                    epsilon = 0.005 * cv2.arcLength(largest_contour, True)
                    simplified_contour = cv2.approxPolyDP(largest_contour, epsilon, True)

                    polygon_points = []
                    for point in simplified_contour:
                        x, y = point[0]
                        polygon_points.append([int(x), int(y)])

                    if polygon_points:
                        self.polygon_data["frames"].append({
                            "frame_id": frame_counter,
                            "grid_position": {"row": r, "col": c},
                            "polygon": polygon_points
                        })
                        detected_count += 1

                        for i in range(len(polygon_points)):
                            p1 = polygon_points[i]
                            p2 = polygon_points[(i + 1) % len(polygon_points)]
                            
                            self.scene.addLine(
                                p1[0] + start_x, p1[1] + start_y,
                                p2[0] + start_x, p2[1] + start_y,
                                polygon_pen
                            )

                frame_counter += 1

        self.btn_export.setEnabled(True)
        self.lbl_info.setText(f"Generierung fertig!\nIn {detected_count} von {frame_counter} Frames wurden Boxen gefunden.")

    def export_to_json(self):
        if not self.polygon_data:
            return

        default_name = os.path.splitext(self.image_path)[0] + "_collision.json"
        file_path, _ = QFileDialog.getSaveFileName(self, "JSON exportieren", default_name, "JSON Files (*.json)")
        
        if file_path:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(self.polygon_data, f, indent=4)
            QMessageBox.information(self, "Erfolg", f"Datei erfolgreich gespeichert unter:\n{file_path}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())