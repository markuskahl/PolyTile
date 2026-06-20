import sys
import os
import json
import cv2
import numpy as np
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QSpinBox, 
                             QFileDialog, QGraphicsScene, QGraphicsView, QMessageBox)
from PyQt6.QtGui import QPixmap, QImage, QPen, QColor
from PyQt6.QtCore import Qt, QLocale

TRANSLATIONS = {
    "de": {
        "window_title": "PolyTile",
        "load_tileset": "1. Tileset laden",
        "grid_settings": "\nGrid-Einstellungen (Pixel):",
        "width": "Breite:",
        "height": "Höhe:",
        "margin": "Seitenabstand (Margin):",
        "spacing": "Abstand (Spacing):",
        "algo_settings": "\nAlgorithmus-Feinjustierung:",
        "alpha_limit": "Alpha-Limit (0-255):",
        "generate_polygons": "2. Polygone generieren",
        "export_json": "3. Als JSON exportieren",
        "controls": "\nSteuerung im Viewer:",
        "controls_desc": "• Mausrad: Zoom In/Out\n• Rechte Maus halten: Bild verschieben",
        "please_load": "\nBitte ein Bild laden...",
        "open_tileset": "Tileset öffnen",
        "images_filter": "Bilder (*.png)",
        "error": "Fehler",
        "error_no_alpha": "Das Bild konnte nicht geladen werden oder besitzt keinen Alpha-Kanal (Transparenz)!",
        "error_save_failed": "Datei konnte nicht gespeichert werden:\n{error}",
        "image_loaded": "Bild geladen: {width}x{height}px\nRaster: {cols}x{rows} Frames.",
        "generation_done": "Generierung fertig!\nIn {detected_count} von {frame_counter} Frames wurden Boxen gefunden.",
        "export_json_title": "JSON exportieren",
        "success": "Erfolg",
        "success_msg": "Datei erfolgreich gespeichert unter:\n{file_path}"
    },
    "en": {
        "window_title": "PolyTile",
        "load_tileset": "1. Load Tileset",
        "grid_settings": "\nGrid Settings (Pixels):",
        "width": "Width:",
        "height": "Height:",
        "margin": "Margin:",
        "spacing": "Spacing:",
        "algo_settings": "\nAlgorithm Fine-Tuning:",
        "alpha_limit": "Alpha Limit (0-255):",
        "generate_polygons": "2. Generate Polygons",
        "export_json": "3. Export as JSON",
        "controls": "\nControls in Viewer:",
        "controls_desc": "• Scroll wheel: Zoom In/Out\n• Hold right click: Move image",
        "please_load": "\nPlease load an image...",
        "open_tileset": "Open Tileset",
        "images_filter": "Images (*.png)",
        "error": "Error",
        "error_no_alpha": "The image could not be loaded or does not have an alpha channel (transparency)!",
        "error_save_failed": "Failed to save file:\n{error}",
        "image_loaded": "Image loaded: {width}x{height}px\nGrid: {cols}x{rows} Frames.",
        "generation_done": "Boxes found in {detected_count} of {frame_counter} frames.",
        "export_json_title": "Export JSON",
        "success": "Success",
        "success_msg": "File successfully saved at:\n{file_path}"
    },
    "fr": {
        "window_title": "PolyTile",
        "load_tileset": "1. Charger le tileset",
        "grid_settings": "\nParamètres de la grille (Pixels) :",
        "width": "Largeur :",
        "height": "Hauteur :",
        "margin": "Marge :",
        "spacing": "Espacement :",
        "algo_settings": "\nAjustement de l'algorithme :",
        "alpha_limit": "Limite alpha (0-255) :",
        "generate_polygons": "2. Générer les polygones",
        "export_json": "3. Exporter en JSON",
        "controls": "\nCommandes du visualiseur :",
        "controls_desc": "• Molette : Zoom avant/arrière\n• Clic droit maintenu : Déplacer l'image",
        "please_load": "\nVeuillez charger une image...",
        "open_tileset": "Ouvrir le tileset",
        "images_filter": "Images (*.png)",
        "error": "Erreur",
        "error_no_alpha": "L'image n'a pas pu être chargée ou ne possède pas de canal alpha (transparence) !",
        "error_save_failed": "Impossible d'enregistrer le fichier :\n{error}",
        "image_loaded": "Image chargée : {width}x{height}px\nGrille : {cols}x{rows} frames.",
        "generation_done": "Génération terminée !\nDes boîtes ont été trouvées dans {detected_count} de {frame_counter} frames.",
        "export_json_title": "Exporter en JSON",
        "success": "Succès",
        "success_msg": "Fichier enregistré avec succès sous :\n{file_path}"
    },
    "es": {
        "window_title": "PolyTile",
        "load_tileset": "1. Cargar tileset",
        "grid_settings": "\nAjustes de cuadrícula (Píxeles):",
        "width": "Ancho:",
        "height": "Alto:",
        "margin": "Margen:",
        "spacing": "Espaciado:",
        "algo_settings": "\nAjuste del algoritmo:",
        "alpha_limit": "Límite alfa (0-255):",
        "generate_polygons": "2. Generar polígonos",
        "export_json": "3. Exportar como JSON",
        "controls": "\nControles en el visor:",
        "controls_desc": "• Rueda del ratón: Zoom +/-\n• Mantener clic derecho: Mover imagen",
        "please_load": "\nPor favor, cargue una imagen...",
        "open_tileset": "Abrir tileset",
        "images_filter": "Imágenes (*.png)",
        "error": "Error",
        "error_no_alpha": "¡No se pudo cargar la imagen o no tiene canal alfa (transparencia)!",
        "error_save_failed": "No se pudo guardar el archivo:\n{error}",
        "image_loaded": "Imagen cargada: {width}x{height}px\nCuadrícula: {cols}x{rows} frames.",
        "generation_done": "¡Generación finalizada!\nSe encontraron cajas en {detected_count} de {frame_counter} frames.",
        "export_json_title": "Exportar JSON",
        "success": "Éxito",
        "success_msg": "Archivo guardado con éxito en:\n{file_path}"
    }
}


class ZoomableGraphicsView(QGraphicsView):
    """ A custom QGraphicsView that supports zoom and panning """
    def __init__(self, scene):
        super().__init__(scene)
        # The buggy QImage line was completely removed here!
        
        # Allows panning the image with the hand (holding mouse wheel / right mouse button)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)

    def wheelEvent(self, event):
        """ Intercepts the scroll wheel to zoom pixel-precisely, with limits """
        zoom_factor = 1.15
        current_zoom = self.transform().m11()
        if event.angleDelta().y() > 0:
            if current_zoom < 50.0:
                self.scale(zoom_factor, zoom_factor)
        else:
            if current_zoom > 0.1:
                self.scale(1.0 / zoom_factor, 1.0 / zoom_factor)

    def mousePressEvent(self, event):
        """ Allows panning with the right mouse button, without blocking normal clicks """
        if event.button() == Qt.MouseButton.RightButton:
            press_event = event.__class__(event.type(), event.position(), event.globalPosition(),
                                          Qt.MouseButton.LeftButton, event.buttons() | Qt.MouseButton.LeftButton,
                                          event.modifiers())
            super().mousePressEvent(press_event)
        else:
            super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        """ Stops panning when the right mouse button is released """
        if event.button() == Qt.MouseButton.RightButton:
            release_event = event.__class__(event.type(), event.position(), event.globalPosition(),
                                            Qt.MouseButton.LeftButton, event.buttons() & ~Qt.MouseButton.LeftButton,
                                            event.modifiers())
            super().mouseReleaseEvent(release_event)
        else:
            super().mouseReleaseEvent(event)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Detect language (default: English)
        system_lang = QLocale.system().name()[:2].lower()
        system_lang = os.environ.get("POLYT_LANG", system_lang).lower()
        self.lang = system_lang if system_lang in TRANSLATIONS else "en"

        self.setWindowTitle(self.t("window_title"))
        self.setGeometry(100, 100, 1024, 768)

        # Status variables
        self.image_path = None
        self.cv_img = None
        self.polygon_data = None

        self.init_ui()

    def t(self, key, **kwargs):
        """ Translation helper """
        text = TRANSLATIONS[self.lang].get(key, key)
        if kwargs:
            return text.format(**kwargs)
        return text

    def init_ui(self):
        main_layout = QHBoxLayout()

        # --- LEFT SIDE: CONTROL PANEL ---
        control_panel = QVBoxLayout()
        control_panel.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        self.btn_load = QPushButton(self.t("load_tileset"))
        self.btn_load.clicked.connect(self.load_image)
        control_panel.addWidget(self.btn_load)
        
        control_panel.addWidget(QLabel(self.t("grid_settings")))
        
        hbox_w = QHBoxLayout()
        hbox_w.addWidget(QLabel(self.t("width")))
        self.spin_width = QSpinBox()
        self.spin_width.setRange(4, 512)
        self.spin_width.setValue(16)
        self.spin_width.valueChanged.connect(self.draw_grid_and_preview)
        hbox_w.addWidget(self.spin_width)
        control_panel.addLayout(hbox_w)

        hbox_h = QHBoxLayout()
        hbox_h.addWidget(QLabel(self.t("height")))
        self.spin_height = QSpinBox()
        self.spin_height.setRange(4, 512)
        self.spin_height.setValue(16)
        self.spin_height.valueChanged.connect(self.draw_grid_and_preview)
        hbox_h.addWidget(self.spin_height)
        control_panel.addLayout(hbox_h)

        hbox_margin = QHBoxLayout()
        hbox_margin.addWidget(QLabel(self.t("margin")))
        self.spin_margin = QSpinBox()
        self.spin_margin.setRange(0, 128)
        self.spin_margin.setValue(0)
        self.spin_margin.valueChanged.connect(self.draw_grid_and_preview)
        hbox_margin.addWidget(self.spin_margin)
        control_panel.addLayout(hbox_margin)

        hbox_spacing = QHBoxLayout()
        hbox_spacing.addWidget(QLabel(self.t("spacing")))
        self.spin_spacing = QSpinBox()
        self.spin_spacing.setRange(0, 128)
        self.spin_spacing.setValue(0)
        self.spin_spacing.valueChanged.connect(self.draw_grid_and_preview)
        hbox_spacing.addWidget(self.spin_spacing)
        control_panel.addLayout(hbox_spacing)

        control_panel.addWidget(QLabel(self.t("algo_settings")))
        
        hbox_t = QHBoxLayout()
        hbox_t.addWidget(QLabel(self.t("alpha_limit")))
        self.spin_thresh = QSpinBox()
        self.spin_thresh.setRange(0, 255)
        self.spin_thresh.setValue(10)
        hbox_t.addWidget(self.spin_thresh)
        control_panel.addLayout(hbox_t)

        self.btn_generate = QPushButton(self.t("generate_polygons"))
        self.btn_generate.setStyleSheet("background-color: #2b579a; color: white; font-weight: bold;")
        self.btn_generate.clicked.connect(self.generate_polygons)
        self.btn_generate.setEnabled(False)
        control_panel.addWidget(self.btn_generate)

        self.btn_export = QPushButton(self.t("export_json"))
        self.btn_export.setStyleSheet("background-color: #1e7145; color: white; font-weight: bold;")
        self.btn_export.clicked.connect(self.export_to_json)
        self.btn_export.setEnabled(False)
        control_panel.addWidget(self.btn_export)

        control_panel.addWidget(QLabel(self.t("controls")))
        control_panel.addWidget(QLabel(self.t("controls_desc")))

        self.lbl_info = QLabel(self.t("please_load"))
        self.lbl_info.setWordWrap(True)
        control_panel.addWidget(self.lbl_info)

        # --- RIGHT SIDE: GRAPHICS VIEW ---
        self.scene = QGraphicsScene()
        self.view = ZoomableGraphicsView(self.scene)

        # Assemble layouts
        control_widget = QWidget()
        control_widget.setLayout(control_panel)
        control_widget.setFixedWidth(260)

        main_layout.addWidget(control_widget)
        main_layout.addWidget(self.view)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def load_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, self.t("open_tileset"), "", self.t("images_filter"))
        if not file_path:
            return

        img = cv2.imread(file_path, cv2.IMREAD_UNCHANGED)

        if img is None or len(img.shape) < 3 or img.shape[2] < 4:
            QMessageBox.critical(self, self.t("error"), self.t("error_no_alpha"))
            return

        self.image_path = file_path
        self.cv_img = img

        self.btn_generate.setEnabled(True)
        self.btn_export.setEnabled(False)
        self.polygon_data = None
        
        self.view.resetTransform()
        self.draw_grid_and_preview()

    def draw_grid_and_preview(self):
        if self.cv_img is None:
            return

        self.btn_export.setEnabled(False)
        self.polygon_data = None

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
        margin = self.spin_margin.value()
        spacing = self.spin_spacing.value()
        
        grid_pen = QPen(QColor(255, 0, 0, 100))
        grid_pen.setWidth(1)
        grid_pen.setStyle(Qt.PenStyle.DashLine)

        cols = max(0, (width - margin + spacing) // (tile_w + spacing)) if (tile_w + spacing) > 0 else 0
        rows = max(0, (height - margin + spacing) // (tile_h + spacing)) if (tile_h + spacing) > 0 else 0

        for r in range(rows):
            for c in range(cols):
                start_x = margin + c * (tile_w + spacing)
                start_y = margin + r * (tile_h + spacing)
                self.scene.addRect(start_x, start_y, tile_w, tile_h, grid_pen)

        self.lbl_info.setText(self.t("image_loaded", width=width, height=height, cols=cols, rows=rows))

    def generate_polygons(self):
        if self.cv_img is None:
            return

        self.draw_grid_and_preview()

        tile_width = self.spin_width.value()
        tile_height = self.spin_height.value()
        margin = self.spin_margin.value()
        spacing = self.spin_spacing.value()
        alpha_thresh = self.spin_thresh.value()

        img_height, img_width = self.cv_img.shape[:2]
        cols = max(0, (img_width - margin + spacing) // (tile_width + spacing)) if (tile_width + spacing) > 0 else 0
        rows = max(0, (img_height - margin + spacing) // (tile_height + spacing)) if (tile_height + spacing) > 0 else 0

        self.polygon_data = {
            "tileset_name": os.path.basename(self.image_path),
            "tile_size": {"width": tile_width, "height": tile_height},
            "margin": margin,
            "spacing": spacing,
            "frames": []
        }

        polygon_pen = QPen(QColor(0, 255, 0, 255))
        polygon_pen.setWidth(2)

        frame_counter = 0
        detected_count = 0

        for r in range(rows):
            for c in range(cols):
                start_x = margin + c * (tile_width + spacing)
                start_y = margin + r * (tile_height + spacing)

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

                    if len(polygon_points) >= 3:
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
        self.lbl_info.setText(self.t("generation_done", detected_count=detected_count, frame_counter=frame_counter))

    def export_to_json(self):
        if not self.polygon_data:
            return

        default_name = os.path.splitext(self.image_path)[0] + "_collision.json"
        file_path, _ = QFileDialog.getSaveFileName(self, self.t("export_json_title"), default_name, "JSON Files (*.json)")
        
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(self.polygon_data, f, indent=4)
                QMessageBox.information(self, self.t("success"), self.t("success_msg", file_path=file_path))
            except Exception as e:
                QMessageBox.critical(self, self.t("error"), self.t("error_save_failed", error=str(e)))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())