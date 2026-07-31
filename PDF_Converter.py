import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QPushButton, QLabel, QFrame, QScrollArea, QFileDialog, QMessageBox,
                            QLineEdit, QComboBox, QGroupBox, QSizePolicy, QGridLayout, QTabWidget)
from PyQt5.QtCore import Qt, QSize, QMimeData, QPoint
from PyQt5.QtGui import QPixmap, QIcon, QPalette, QColor, QDrag, QFont

# Import Pillow dengan error handling
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# Import PyPDF2 untuk manipulasi PDF
try:
    import PyPDF2
    from PyPDF2 import PdfMerger, PdfReader
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False

class DraggableLabel(QLabel):
    def __init__(self, parent_widget, index):
        super().__init__(parent_widget)
        self.parent_widget = parent_widget
        self.index = index
        self.setFixedSize(20, 20)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("""
            QLabel {
                color: #666;
                font-size: 20px;
                padding: 2px;
                background-color: #f0f0f0;
                border-radius: 3px;
            }
        """)
        self.setText("≡")
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.parent_widget.start_drag(self.index, event.pos())
            
    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            self.parent_widget.start_drag(self.index, event.pos())

class ImagePreviewWidget(QFrame):
    def __init__(self, file_path, index, parent=None, is_pdf=False):
        super().__init__(parent)
        self.file_path = file_path
        self.index = index
        self.parent = parent
        self.is_selected = False
        self.is_pdf = is_pdf
        self.drag_start_position = QPoint()
        
        self.setup_ui()
        self.load_content()
        
    def setup_ui(self):
        self.setFrameStyle(QFrame.Box)
        self.setLineWidth(1)
        self.setFixedSize(200, 240)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setAcceptDrops(True)
        
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(5)
        main_layout.setContentsMargins(8, 8, 8, 8)
        
        # Header dengan drag handle dan nomor
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 5)
        
        # Drag handle icon (sekarang sebagai widget terpisah)
        self.drag_handle = DraggableLabel(self, self.index)
        header_layout.addWidget(self.drag_handle)
        
        # Nomor urutan
        self.order_label = QLabel(f"#{self.index + 1}")
        self.order_label.setStyleSheet("""
            QLabel {
                color: #007acc;
                font-weight: bold;
                font-size: 20px;
                background-color: #e3f2fd;
                padding: 2px 6px;
                border-radius: 3px;
            }
        """)
        self.order_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(self.order_label)
        
        # File type indicator
        file_type_label = QLabel("📄" if self.is_pdf else "🖼️")
        file_type_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(file_type_label)
        
        header_layout.addStretch()
        main_layout.addLayout(header_layout)
        
        # Preview area
        preview_frame = QFrame()
        preview_frame.setStyleSheet("border: 1px solid #ccc; background-color: #f8f8f8; border-radius: 3px;")
        preview_layout = QVBoxLayout(preview_frame)
        preview_layout.setContentsMargins(2, 2, 2, 2)
        
        self.preview_label = QLabel()
        self.preview_label.setFixedSize(140, 140)
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setStyleSheet("background-color: transparent;")
        preview_layout.addWidget(self.preview_label)
        
        main_layout.addWidget(preview_frame)
        
        # Nama file
        self.name_label = QLabel()
        self.name_label.setStyleSheet("""
            QLabel {
                font-weight: bold;
                font-size: 20px;
                color: #333;
                background-color: transparent;
            }
        """)
        self.name_label.setWordWrap(True)
        self.name_label.setMaximumHeight(30)
        self.name_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.name_label)
        
        # Info
        self.info_label = QLabel()
        self.info_label.setStyleSheet("""
            QLabel {
                font-size: 15px;
                color: #666;
                background-color: transparent;
            }
        """)
        self.info_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.info_label)
        
        # Delete button
        self.delete_btn = QPushButton("🗑️")
        self.delete_btn.setFixedSize(30, 30)
        self.delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff6b6b;
                color: white;
                border: none;
                border-radius: 15px;
                font-size: 20px;
            }
            QPushButton:hover {
                background-color: #ee5253;
            }
            QPushButton:pressed {
                background-color: #d63031;
            }
        """)
        self.delete_btn.clicked.connect(self.delete_file)
        main_layout.addWidget(self.delete_btn, alignment=Qt.AlignCenter)
        
        self.update_selection(False)
        
    def load_content(self):
        try:
            filename = os.path.basename(self.file_path)
            if len(filename) > 18:
                filename = filename[:15] + "..."
            
            self.name_label.setText(filename)
            
            if self.is_pdf:
                # Handle PDF files
                if PYPDF2_AVAILABLE:
                    with open(self.file_path, 'rb') as f:
                        pdf_reader = PdfReader(f)
                        num_pages = len(pdf_reader.pages)
                        self.info_label.setText(f"{num_pages} pages")
                else:
                    self.info_label.setText("PDF info unavailable")
                
                # Set PDF icon
                self.preview_label.setText("📄\nPDF")
                self.preview_label.setStyleSheet("font-size: 40px;")
                
            else:
                # Handle image files
                if PIL_AVAILABLE:
                    img = Image.open(self.file_path)
                    dimensions = f"{img.size[0]} × {img.size[1]} px"
                    self.info_label.setText(dimensions)
                    
                    # Create thumbnail
                    img.thumbnail((140, 140), Image.LANCZOS if hasattr(Image, 'LANCZOS') else Image.ANTIALIAS)
                    img.save("temp_thumbnail.png", "PNG")
                    
                    pixmap = QPixmap("temp_thumbnail.png")
                    self.preview_label.setPixmap(pixmap)
                    
                    # Clean up temp file
                    if os.path.exists("temp_thumbnail.png"):
                        os.remove("temp_thumbnail.png")
                else:
                    self.preview_label.setText("Image")
                    self.info_label.setText("PIL not available")
                    
        except Exception as e:
            self.preview_label.setText("Error")
            self.name_label.setText("Load Error")
            self.info_label.setText("Failed to load")
            
    def start_drag(self, index, pos):
        """Memulai operasi drag dari widget ini"""
        self.drag_start_position = pos
        if self.parent:
            self.parent.select_file(index)
            
        # Buat objek drag
        drag = QDrag(self)
        mime_data = QMimeData()
        mime_data.setText(str(index))
        drag.setMimeData(mime_data)
        
        # Ubah tampilan selama drag
        self.setStyleSheet("""
            QFrame {
                border: 2px solid #ff9f43;
                background-color: #fff9f0;
                border-radius: 6px;
            }
        """)
        
        # Jalankan drag operation
        drag.exec_(Qt.MoveAction)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.parent:
                self.parent.select_file(self.index)
        super().mousePressEvent(event)
        
    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()
            
    def dropEvent(self, event):
        if event.mimeData().hasText():
            source_index = int(event.mimeData().text())
            if self.parent:
                self.parent.move_file(source_index, self.index)
            event.acceptProposedAction()
            
    def delete_file(self):
        if self.parent:
            self.parent.remove_file(self.index)
        
    def update_selection(self, selected):
        self.is_selected = selected
        if selected:
            self.setStyleSheet("""
                QFrame {
                    border: 2px solid #3498db;
                    background-color: #e8f4fd;
                    border-radius: 6px;
                }
            """)
        else:
            self.setStyleSheet("""
                QFrame {
                    border: 1px solid #ddd;
                    background-color: white;
                    border-radius: 6px;
                }
            """)
            
    def update_index(self, new_index):
        self.index = new_index
        self.order_label.setText(f"#{self.index + 1}")
        self.drag_handle.index = new_index  # Perbarui juga index di drag handle

class EnhancedImageToPDFConverter(QMainWindow):
    def __init__(self):
        super().__init__()
        self.file_paths = []
        self.selected_index = -1
        self.preview_widgets = []
        
        self.setup_ui()
        
        if not PIL_AVAILABLE:
            QMessageBox.warning(self, "Warning", 
                "Pillow library is required for image processing. Please install it using: pip install Pillow")
        
        if not PYPDF2_AVAILABLE:
            QMessageBox.warning(self, "Warning", 
                "PyPDF2 library is required for PDF merging. Please install it using: pip install PyPDF2")
    
    def setup_ui(self):
        self.setWindowTitle("PDF & Image Toolbox")
        self.setGeometry(100, 100, 1300, 800)
        
        # Menghapus tombol maximize dari window
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowMaximizeButtonHint)
        
        # Set application font
        font = QFont("Segoe UI", 9)
        QApplication.setFont(font)
        
        # Central widget dengan tab
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                background: #f8f9fa;
            }
            QTabBar::tab {
                background: #ecf0f1;
                border: 1px solid #bdc3c7;
                padding: 8px 16px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background: #3498db;
                color: white;
                border-bottom-color: #3498db;
            }
            QTabBar::tab:hover:!selected {
                background: #d6dbdf;
            }
        """)
        
        # Tab 1: Image to PDF
        self.image_tab = QWidget()
        self.setup_image_tab()
        self.tab_widget.addTab(self.image_tab, "🖼️ Image to PDF")
        
        # Tab 2: PDF Merger
        self.pdf_tab = QWidget()
        self.setup_pdf_tab()
        self.tab_widget.addTab(self.pdf_tab, "📄 Merge PDFs")
        
        main_layout.addWidget(self.tab_widget)
    
    def setup_image_tab(self):
        layout = QHBoxLayout(self.image_tab)
        layout.setSpacing(20)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Left panel (controls)
        left_panel = QWidget()
        left_panel.setFixedWidth(320)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(15)
        
        # Title
        title_label = QLabel("Image to PDF Converter")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: white;
                padding: 15px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3498db, stop:1 #2c3e50);
                border-radius: 8px;
                qproperty-alignment: AlignCenter;
            }
        """)
        left_layout.addWidget(title_label)
        
        # Control buttons
        control_group = QGroupBox("🛠️ Controls")
        control_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 20px;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                color: #2c3e50;
            }
        """)
        control_layout = QVBoxLayout(control_group)
        control_layout.setSpacing(10)
        
        self.btn_select_images = QPushButton("📁 Select Images")
        self.btn_select_images.clicked.connect(lambda: self.select_files(False))
        
        self.btn_clear_images = QPushButton("🗑️ Clear All")
        self.btn_clear_images.clicked.connect(self.clear_all)
        
        for btn in [self.btn_select_images, self.btn_clear_images]:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border: none;
                    padding: 10px;
                    border-radius: 6px;
                    font-weight: bold;
                    font-size: 20px;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
                QPushButton:pressed {
                    background-color: #21618c;
                }
                QPushButton:disabled {
                    background-color: #bdc3c7;
                }
            """)
            control_layout.addWidget(btn)
        
        # Instructions
        instructions = QLabel(
            "• Click image to select\n"
            "• Drag ≡ handle to reorder\n"
            "• Click 🗑️ to delete image\n"
            "• Multiple selection: Ctrl+Click"
        )
        instructions.setStyleSheet("""
            QLabel {
                color: #7f8c8d;
                font-size: 15px;
                padding: 12px;
                background-color: #f8f9fa;
                border-radius: 6px;
                border: 1px solid #e0e0e0;
            }
        """)
        instructions.setWordWrap(True)
        control_layout.addWidget(instructions)
        
        left_layout.addWidget(control_group)
        
        # PDF options
        options_group = QGroupBox("⚙️ PDF Options")
        options_group.setStyleSheet(control_group.styleSheet())
        options_layout = QVBoxLayout(options_group)
        options_layout.setSpacing(8)
        
        # PDF title
        options_layout.addWidget(QLabel("PDF Title:"))
        self.pdf_title = QLineEdit("Combined Images")
        self.pdf_title.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                font-size: 20px;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
        """)
        options_layout.addWidget(self.pdf_title)
        
        # Page size
        options_layout.addWidget(QLabel("Page Size:"))
        self.page_size = QComboBox()
        self.page_size.addItems(["Original", "A4", "Letter", "Legal", "A3", "A5"])
        self.page_size.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                font-size: 20px;
            }
            QComboBox:focus {
                border-color: #3498db;
            }
        """)
        options_layout.addWidget(self.page_size)
        
        # Orientation
        options_layout.addWidget(QLabel("Orientation:"))
        self.orientation = QComboBox()
        self.orientation.addItems(["Portrait", "Landscape"])
        self.orientation.setStyleSheet(self.page_size.styleSheet())
        options_layout.addWidget(self.orientation)
        
        left_layout.addWidget(options_group)
        
        # Convert button
        self.btn_convert = QPushButton("🔄 Convert to PDF")
        self.btn_convert.clicked.connect(self.convert_to_pdf)
        self.btn_convert.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #9b59b6, stop:1 #8e44ad);
                color: white;
                border: none;
                padding: 14px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 20px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #8e44ad, stop:1 #7d3c98);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #7d3c98, stop:1 #6c3483);
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """)
        left_layout.addWidget(self.btn_convert)
        
        # Status label
        self.status_label_images = QLabel("Select images to begin")
        self.status_label_images.setStyleSheet("""
            QLabel {
                color: #7f8c8d;
                font-style: italic;
                font-size: 20px;
                padding: 8px;
                background-color: #f8f9fa;
                border-radius: 5px;
                border: 1px solid #e0e0e0;
            }
        """)
        self.status_label_images.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(self.status_label_images)
        
        left_layout.addStretch()
        layout.addWidget(left_panel)
        
        # Right panel (preview)
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setSpacing(12)
        
        preview_label = QLabel("📷 Image Preview")
        preview_label.setStyleSheet("""
            QLabel {
                font-size: 25px;
                font-weight: bold;
                color: #2c3e50;
                padding: 12px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #ecf0f1, stop:1 #dfe6e9);
                border-radius: 8px;
                border: 1px solid #bdc3c7;
            }
        """)
        preview_label.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(preview_label)
        
        # Scroll area for previews
        self.scroll_area_images = QScrollArea()
        self.scroll_area_images.setWidgetResizable(True)
        self.scroll_area_images.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area_images.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area_images.setStyleSheet("""
            QScrollArea {
                border: 1px solid #bdc3c7;
                border-radius: 6px;
                background-color: #f8f9fa;
            }
        """)
        
        self.scroll_content_images = DropArea(self, is_pdf=False)
        self.grid_layout_images = QGridLayout(self.scroll_content_images)
        self.grid_layout_images.setSpacing(15)
        self.grid_layout_images.setContentsMargins(15, 15, 15, 15)
        
        self.scroll_area_images.setWidget(self.scroll_content_images)
        right_layout.addWidget(self.scroll_area_images)
        
        layout.addWidget(right_panel, 1)
    
    def setup_pdf_tab(self):
        layout = QHBoxLayout(self.pdf_tab)
        layout.setSpacing(20)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Left panel (controls)
        left_panel = QWidget()
        left_panel.setFixedWidth(320)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(15)
        
        # Title
        title_label = QLabel("PDF Merger")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: white;
                padding: 15px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #e74c3c, stop:1 #c0392b);
                border-radius: 8px;
                qproperty-alignment: AlignCenter;
            }
        """)
        left_layout.addWidget(title_label)
        
        # Control buttons
        control_group = QGroupBox("🛠️ Controls")
        control_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 20px;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                color: #2c3e50;
            }
        """)
        control_layout = QVBoxLayout(control_group)
        control_layout.setSpacing(10)
        
        self.btn_select_pdfs = QPushButton("📁 Select PDFs")
        self.btn_select_pdfs.clicked.connect(lambda: self.select_files(True))
        
        self.btn_clear_pdfs = QPushButton("🗑️ Clear All")
        self.btn_clear_pdfs.clicked.connect(self.clear_all_pdfs)
        
        for btn in [self.btn_select_pdfs, self.btn_clear_pdfs]:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #e74c3c;
                    color: white;
                    border: none;
                    padding: 10px;
                    border-radius: 6px;
                    font-weight: bold;
                    font-size: 20px;
                }
                QPushButton:hover {
                    background-color: #c0392b;
                }
                QPushButton:pressed {
                    background-color: #a93226;
                }
                QPushButton:disabled {
                    background-color: #bdc3c7;
                }
            """)
            control_layout.addWidget(btn)
        
        # Instructions
        instructions = QLabel(
            "• Click PDF to select\n"
            "• Drag ≡ handle to reorder\n"
            "• Click 🗑️ to delete PDF\n"
            "• Multiple selection: Ctrl+Click"
        )
        instructions.setStyleSheet("""
            QLabel {
                color: #7f8c8d;
                font-size: 15px;
                padding: 12px;
                background-color: #f8f9fa;
                border-radius: 6px;
                border: 1px solid #e0e0e0;
            }
        """)
        instructions.setWordWrap(True)
        control_layout.addWidget(instructions)
        
        left_layout.addWidget(control_group)
        
        # Merge button
        self.btn_merge = QPushButton("🔗 Merge PDFs")
        self.btn_merge.clicked.connect(self.merge_pdfs)
        self.btn_merge.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #9b59b6, stop:1 #8e44ad);
                color: white;
                border: none;
                padding: 14px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 20px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #8e44ad, stop:1 #7d3c98);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #7d3c98, stop:1 #6c3483);
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """)
        left_layout.addWidget(self.btn_merge)
        
        # Status label
        self.status_label_pdfs = QLabel("Select PDFs to begin")
        self.status_label_pdfs.setStyleSheet("""
            QLabel {
                color: #7f8c8d;
                font-style: italic;
                font-size: 20px;
                padding: 8px;
                background-color: #f8f9fa;
                border-radius: 5px;
                border: 1px solid #e0e0e0;
            }
        """)
        self.status_label_pdfs.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(self.status_label_pdfs)
        
        left_layout.addStretch()
        layout.addWidget(left_panel)
        
        # Right panel (preview)
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setSpacing(12)
        
        preview_label = QLabel("📄 PDF Preview")
        preview_label.setStyleSheet("""
            QLabel {
                font-size: 25px;
                font-weight: bold;
                color: #2c3e50;
                padding: 12px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #ecf0f1, stop:1 #dfe6e9);
                border-radius: 8px;
                border: 1px solid #bdc3c7;
            }
        """)
        preview_label.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(preview_label)
        
        # Scroll area for previews
        self.scroll_area_pdfs = QScrollArea()
        self.scroll_area_pdfs.setWidgetResizable(True)
        self.scroll_area_pdfs.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area_pdfs.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area_pdfs.setStyleSheet("""
            QScrollArea {
                border: 1px solid #bdc3c7;
                border-radius: 6px;
                background-color: #f8f9fa;
            }
        """)
        
        self.scroll_content_pdfs = DropArea(self, is_pdf=True)
        self.grid_layout_pdfs = QGridLayout(self.scroll_content_pdfs)
        self.grid_layout_pdfs.setSpacing(15)
        self.grid_layout_pdfs.setContentsMargins(15, 15, 15, 15)
        
        self.scroll_area_pdfs.setWidget(self.scroll_content_pdfs)
        right_layout.addWidget(self.scroll_area_pdfs)
        
        layout.addWidget(right_panel, 1)
    
    def select_files(self, is_pdf):
        if is_pdf and not PYPDF2_AVAILABLE:
            QMessageBox.critical(self, "Error", "PyPDF2 library is not available. Please install it first.")
            return
            
        if not is_pdf and not PIL_AVAILABLE:
            QMessageBox.critical(self, "Error", "Pillow library is not available. Please install it first.")
            return
            
        file_filter = "PDF Files (*.pdf)" if is_pdf else "Image Files (*.png *.jpg *.jpeg *.bmp *.tiff *.webp)"
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Files",
            "",
            f"{file_filter};;All Files (*)"
        )
        
        if files:
            current_tab_files = []
            for file in files:
                if file not in self.file_paths:
                    self.file_paths.append((file, is_pdf))
                    current_tab_files.append((file, is_pdf))
            
            status_text = f"📄 {len(current_tab_files)} {'PDFs' if is_pdf else 'images'} selected"
            if is_pdf:
                self.status_label_pdfs.setText(status_text)
            else:
                self.status_label_images.setText(status_text)
            
            self.update_preview(is_pdf)
    
    def remove_file(self, index):
        if 0 <= index < len(self.file_paths):
            is_pdf = self.file_paths[index][1]
            self.file_paths.pop(index)
            self.selected_index = -1
            
            # Count remaining files of this type
            count = sum(1 for _, file_is_pdf in self.file_paths if file_is_pdf == is_pdf)
            status_text = f"📄 {count} {'PDFs' if is_pdf else 'images'} remaining"
            
            if is_pdf:
                self.status_label_pdfs.setText(status_text)
            else:
                self.status_label_images.setText(status_text)
                
            self.update_preview(is_pdf)
    
    def clear_all(self):
        # Hapus hanya file gambar
        self.file_paths = [fp for fp in self.file_paths if fp[1]]  # Keep only PDFs
        self.selected_index = -1
        self.status_label_images.setText("Select images to begin")
        self.update_preview(False)
    
    def clear_all_pdfs(self):
        # Hapus hanya file PDF
        self.file_paths = [fp for fp in self.file_paths if not fp[1]]  # Keep only images
        self.selected_index = -1
        self.status_label_pdfs.setText("Select PDFs to begin")
        self.update_preview(True)
    
    def move_file(self, from_index, to_index):
        if 0 <= from_index < len(self.file_paths) and 0 <= to_index < len(self.file_paths):
            # Move the file
            file = self.file_paths.pop(from_index)
            self.file_paths.insert(to_index, file)
            
            # Update selection
            self.selected_index = to_index
            is_pdf = file[1]
            self.update_preview(is_pdf)
    
    def select_file(self, index):
        self.selected_index = index
        is_pdf = self.file_paths[index][1] if index < len(self.file_paths) else False
        self.update_preview(is_pdf)
    
    def update_preview(self, is_pdf):
        # Determine which grid layout to use
        if is_pdf:
            grid_layout = self.grid_layout_pdfs
            scroll_content = self.scroll_content_pdfs
        else:
            grid_layout = self.grid_layout_images
            scroll_content = self.scroll_content_images
        
        # Clear existing previews
        for i in reversed(range(grid_layout.count())):
            item = grid_layout.itemAt(i)
            if item.widget():
                item.widget().deleteLater()
        
        # Get files for this tab
        tab_files = [(path, idx) for idx, (path, file_is_pdf) in enumerate(self.file_paths) if file_is_pdf == is_pdf]
        
        if not tab_files:
            # Show message when no files
            no_files_label = QLabel(f"No {'PDFs' if is_pdf else 'images'} selected\n\nClick 'Select {'PDFs' if is_pdf else 'Images'}' to add files")
            no_files_label.setAlignment(Qt.AlignCenter)
            no_files_label.setStyleSheet("""
                QLabel {
                    font-size: 20px;
                    color: #7f8c8d;
                    padding: 60px;
                    background-color: transparent;
                }
            """)
            grid_layout.addWidget(no_files_label, 0, 0, 1, 1)
            return
        
        # Calculate grid position - 4 columns
        cols = 4
        for i, (file_path, original_index) in enumerate(tab_files):
            row = i // cols
            col = i % cols
            
            preview_widget = ImagePreviewWidget(file_path, original_index, self, is_pdf)
            preview_widget.update_selection(original_index == self.selected_index)
            grid_layout.addWidget(preview_widget, row, col, Qt.AlignCenter)
    
    def convert_to_pdf(self):
        if not PIL_AVAILABLE:
            QMessageBox.critical(self, "Error", "Pillow library is not available. Please install it first.")
            return
            
        # Get only image files
        image_files = [path for path, is_pdf in self.file_paths if not is_pdf]
        
        if not image_files:
            QMessageBox.warning(self, "Warning", "Please select images first")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save PDF As",
            "",
            "PDF Files (*.pdf);;All Files (*)"
        )
        
        if file_path:
            try:
                # Ensure .pdf extension
                if not file_path.lower().endswith('.pdf'):
                    file_path += '.pdf'
                
                images = []
                page_size = self.page_size.currentText()
                orientation = self.orientation.currentText()
                
                for img_path in image_files:
                    img = Image.open(img_path)
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                    
                    if page_size == "Original":
                        images.append(img)
                    else:
                        sizes = {
                            "A4": (2480, 3508),
                            "Letter": (2550, 3300),
                            "Legal": (2550, 4200),
                            "A3": (3508, 4961),
                            "A5": (1748, 2480)
                        }
                        size = sizes.get(page_size, img.size)
                        if orientation == "Landscape":
                            size = (size[1], size[0])
                        img = img.resize(size, Image.LANCZOS if hasattr(Image, 'LANCZOS') else Image.ANTIALIAS)
                        images.append(img)
                
                if images:
                    images[0].save(
                        file_path,
                        save_all=True,
                        append_images=images[1:],
                        title=self.pdf_title.text(),
                    )
                    
                    QMessageBox.information(self, "Success", f"✅ PDF successfully created")
                    self.status_label_images.setText("Conversion completed ✅")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"❌ An error occurred: {str(e)}")

    def merge_pdfs(self):
        if not PYPDF2_AVAILABLE:
            QMessageBox.critical(self, "Error", "PyPDF2 library is not available. Please install it first.")
            return
            
        # Get only PDF files
        pdf_files = [path for path, is_pdf in self.file_paths if is_pdf]
        
        if len(pdf_files) < 2:
            QMessageBox.warning(self, "Warning", "Please select at least 2 PDF files to merge")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Merged PDF As",
            "",
            "PDF Files (*.pdf);;All Files (*)"
        )
        
        if file_path:
            try:
                # Ensure .pdf extension
                if not file_path.lower().endswith('.pdf'):
                    file_path += '.pdf'
                
                merger = PdfMerger()
                
                for pdf_path in pdf_files:
                    merger.append(pdf_path)
                
                merger.write(file_path)
                merger.close()
                
                QMessageBox.information(self, "Success", f"✅ PDFs successfully merged")
                self.status_label_pdfs.setText("Merge completed ✅")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"❌ An error occurred: {str(e)}")

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        files = []
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.webp', '.pdf')):
                is_pdf = file_path.lower().endswith('.pdf')
                files.append((file_path, is_pdf))
        
        if files:
            current_tab = self.tab_widget.currentIndex()  # 0 for images, 1 for PDFs
            current_is_pdf = (current_tab == 1)
            
            for file_path, is_pdf in files:
                if is_pdf == current_is_pdf and (file_path, is_pdf) not in self.file_paths:
                    self.file_paths.append((file_path, is_pdf))
            
            count = sum(1 for _, file_is_pdf in self.file_paths if file_is_pdf == current_is_pdf)
            status_text = f"📄 {count} {'PDFs' if current_is_pdf else 'images'} selected"
            
            if current_is_pdf:
                self.status_label_pdfs.setText(status_text)
            else:
                self.status_label_images.setText(status_text)
                
            self.update_preview(current_is_pdf)

class DropArea(QWidget):
    def __init__(self, parent, is_pdf):
        super().__init__()
        self.parent = parent
        self.is_pdf = is_pdf
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        files = []
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if self.is_pdf:
                if file_path.lower().endswith('.pdf'):
                    files.append((file_path, True))
            else:
                if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.webp')):
                    files.append((file_path, False))
        if files:
            for file_path, is_pdf in files:
                if (file_path, is_pdf) not in self.parent.file_paths:
                    self.parent.file_paths.append((file_path, is_pdf))
            count = sum(1 for _, file_is_pdf in self.parent.file_paths if file_is_pdf == self.is_pdf)
            status_text = f"📄 {count} {'PDFs' if self.is_pdf else 'images'} selected"
            if self.is_pdf:
                self.parent.status_label_pdfs.setText(status_text)
            else:
                self.parent.status_label_images.setText(status_text)
            self.parent.update_preview(self.is_pdf)

def main():
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Create and show the main window
    converter = EnhancedImageToPDFConverter()
    converter.show()
    
    # Run the application
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()