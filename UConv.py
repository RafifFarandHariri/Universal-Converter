import sys
import os
import tempfile
from io import BytesIO
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                            QPushButton, QLabel, QFrame, QScrollArea, QFileDialog, QMessageBox,
                            QLineEdit, QComboBox, QGroupBox, QSizePolicy, QGridLayout,
                            QTableWidget, QTableWidgetItem, QHeaderView, QListWidget, QListWidgetItem,
                            QTextEdit, QAbstractItemView, QSplitter, QRadioButton, QButtonGroup,
                            QSlider, QSpinBox, QStackedWidget, QMenu)
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
    from PyPDF2 import PdfMerger, PdfReader, PdfWriter
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False

# Import reportlab untuk watermark
try:
    from reportlab.pdfgen import canvas as rl_canvas
    from reportlab.lib.colors import Color
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

# Import PyMuPDF (fitz) untuk render PDF -> JPG (tidak butuh binary eksternal)
try:
    import fitz  # PyMuPDF
    FITZ_AVAILABLE = True
except ImportError:
    FITZ_AVAILABLE = False

RED = "#c0392b"
RED_DARK = "#922b21"
RED_LIGHT = "#e74c3c"
BLACK = "#1c1c1c"
BLACK_SOFT = "#2b2b2b"
WHITE = "#ffffff"
OFFWHITE = "#f7f7f7"
BORDER = "#d9d9d9"
MUTED = "#6b6b6b"

HEADER_LABEL_STYLE = f"""
    QLabel {{
        font-size: 15px;
        font-weight: bold;
        color: {WHITE};
        padding: 6px 10px;
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 {BLACK}, stop:1 {RED});
        border-radius: 6px;
    }}
"""

GROUPBOX_STYLE = f"""
    QGroupBox {{
        font-weight: bold;
        font-size: 16px;
        color: {BLACK};
        border: 2px solid {RED};
        border-radius: 8px;
        margin-top: 10px;
        padding-top: 15px;
        background: {WHITE};
    }}
    QGroupBox::title {{
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 8px 0 8px;
        color: {RED_DARK};
    }}
"""

RED_BUTTON_STYLE = f"""
    QPushButton {{
        background-color: {RED};
        color: {WHITE};
        border: none;
        padding: 10px;
        border-radius: 6px;
        font-weight: bold;
        font-size: 15px;
    }}
    QPushButton:hover {{
        background-color: {RED_DARK};
    }}
    QPushButton:pressed {{
        background-color: #7b241c;
    }}
    QPushButton:disabled {{
        background-color: #bdbdbd;
    }}
"""

BLACK_BUTTON_STYLE = f"""
    QPushButton {{
        background-color: {BLACK};
        color: {WHITE};
        border: none;
        padding: 10px;
        border-radius: 6px;
        font-weight: bold;
        font-size: 15px;
    }}
    QPushButton:hover {{
        background-color: {BLACK_SOFT};
    }}
    QPushButton:pressed {{
        background-color: #000000;
    }}
    QPushButton:disabled {{
        background-color: #bdbdbd;
    }}
"""

ACTION_BUTTON_STYLE = f"""
    QPushButton {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 {RED}, stop:1 {BLACK});
        color: {WHITE};
        border: none;
        padding: 14px;
        border-radius: 6px;
        font-weight: bold;
        font-size: 16px;
    }}
    QPushButton:hover {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 {RED_DARK}, stop:1 {BLACK_SOFT});
    }}
    QPushButton:pressed {{
        background: {BLACK};
    }}
    QPushButton:disabled {{
        background-color: #bdbdbd;
    }}
"""

INPUT_STYLE = f"""
    QLineEdit, QComboBox, QSpinBox {{
        padding: 8px;
        border: 2px solid {BORDER};
        border-radius: 5px;
        font-size: 14px;
        background: {WHITE};
        color: {BLACK};
    }}
    QLineEdit:focus, QComboBox:focus, QSpinBox:focus {{
        border-color: {RED};
    }}
"""

STATUS_LABEL_STYLE = f"""
    QLabel {{
        color: {MUTED};
        font-style: italic;
        font-size: 14px;
        padding: 8px;
        background-color: {OFFWHITE};
        border-radius: 5px;
        border: 1px solid {BORDER};
    }}
"""

TITLE_BANNER_STYLE = f"""
    QLabel {{
        font-size: 18px;
        font-weight: bold;
        color: {WHITE};
        padding: 15px;
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 {BLACK}, stop:1 {RED});
        border-radius: 8px;
        qproperty-alignment: AlignCenter;
    }}
"""

LIST_STYLE = f"""
    QListWidget {{
        border: 1px solid {BORDER};
        border-radius: 6px;
        background-color: {WHITE};
        alternate-background-color: {OFFWHITE};
        color: {BLACK};
    }}
    QListWidget::item {{
        padding: 8px;
    }}
    QListWidget::item:selected {{
        background: {RED};
        color: {WHITE};
    }}
"""

TABLE_STYLE = f"""
    QTableWidget {{
        border: 1px solid {BORDER};
        border-radius: 6px;
        background-color: {WHITE};
        alternate-background-color: {OFFWHITE};
        selection-background-color: {RED};
        selection-color: {WHITE};
        color: {BLACK};
    }}
    QTableWidget::item {{
        padding: 8px;
    }}
    QTableWidget::item:selected {{
        background: {RED};
        color: {WHITE};
    }}
"""


HOME_BG = "#0f0f0f"
CARD_BG = "#1a1a1a"
CARD_BG_DISABLED = "#141414"
CARD_BORDER = "#2c2c2c"
CARD_TITLE = "#ffffff"
CARD_TITLE_DISABLED = "#7a7a7a"
CARD_DESC = "#a8a8a8"
CARD_DESC_DISABLED = "#555555"

SUPPORTED_IMAGE_EXTS = ('.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.webp', '.gif')
SUPPORTED_PDF_EXTS = ('.pdf',)


class ToolCard(QFrame):
    """
    Satu kartu fitur di halaman Beranda (mirip kartu di iLovePDF).
    Kalau `enabled=True` kartu bisa diklik dan memanggil `on_click`.
    Kalau `enabled=False` kartu tetap kelihatan tapi ditandai
    "Segera Hadir" dan klik-nya cuma menampilkan info, bukan error,
    supaya user tahu fitur itu memang belum diimplementasikan.
    """
    def __init__(self, icon, title, desc, badge_color, enabled=True, on_click=None):
        super().__init__()
        self.enabled = enabled
        self.on_click = on_click
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumSize(220, 160)
        self.setStyleSheet(f"""
            QFrame {{
                background: {CARD_BG if enabled else CARD_BG_DISABLED};
                border-radius: 10px;
                border: 1px solid {CARD_BORDER};
            }}
            QFrame:hover {{
                border: 1px solid {RED if enabled else CARD_BORDER};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 16)
        layout.setSpacing(8)

        icon_label = QLabel(icon)
        icon_label.setFixedSize(44, 44)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet(f"""
            QLabel {{
                font-size: 18px;
                background: {badge_color if enabled else '#333333'};
                color: {WHITE};
                border-radius: 8px;
            }}
        """)
        layout.addWidget(icon_label)

        title_label = QLabel(title)
        title_label.setWordWrap(True)
        title_label.setStyleSheet(f"""
            color: {CARD_TITLE if enabled else CARD_TITLE_DISABLED};
            font-size: 15px;
            font-weight: bold;
        """)
        layout.addWidget(title_label)

        desc_label = QLabel(desc)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet(f"""
            color: {CARD_DESC if enabled else CARD_DESC_DISABLED};
            font-size: 12px;
        """)
        layout.addWidget(desc_label)

        layout.addStretch()

        if not enabled:
            badge = QLabel("🕒 Segera Hadir")
            badge.setStyleSheet(f"color: {RED_LIGHT}; font-size: 11px; font-weight: bold;")
            layout.addWidget(badge)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.on_click:
            self.on_click()
        super().mousePressEvent(event)


class NoScrollComboBox(QComboBox):
    """
    QComboBox secara default menangkap wheel event dan memakainya untuk
    mengganti index/value saat mouse berada di atasnya. Override
    wheelEvent supaya event di-ignore() saja, jadi scroll mouse di atas
    combo box tidak mengubah pilihan tanpa sengaja.
    """
    def wheelEvent(self, event):
        event.ignore()


class ReorderableFileTable(QTableWidget):
    """
    QTableWidget's built-in InternalMove drag-and-drop only moves individual
    cells, not whole rows - for a multi-column table like this one that
    corrupts the row data (columns end up mismatched / values vanish), which
    is exactly the bug seen when reordering files. So we don't call
    super().dropEvent() at all; instead we figure out the source row (the
    row that was selected when the drag started) and the target row (the
    row under the mouse on drop), and ask the parent window to reorder its
    underlying file list directly. The table is then fully rebuilt from
    that list, so it can never end up in an inconsistent state.
    """
    def __init__(self, parent_window, is_pdf):
        super().__init__(parent_window)
        self.parent_window = parent_window
        self.is_pdf = is_pdf
        self._drag_source_row = -1

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            index = self.indexAt(event.pos())
            self._drag_source_row = index.row() if index.isValid() else -1
        super().mousePressEvent(event)

    def dropEvent(self, event):
        if event.source() is not self:
            event.ignore()
            return

        source_row = self._drag_source_row if self._drag_source_row >= 0 else self.currentRow()
        target_index = self.indexAt(event.pos())
        target_row = target_index.row() if target_index.isValid() else self.rowCount() - 1

        event.setDropAction(Qt.IgnoreAction)
        event.accept()

        if self.parent_window and source_row != target_row:
            self.parent_window.reorder_files(self.is_pdf, source_row, target_row)
        self._drag_source_row = -1


def pil_image_to_pixmap(image, target_size=None):
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    pixmap = QPixmap()
    pixmap.loadFromData(buffer.getvalue(), "PNG")
    if target_size:
        pixmap = pixmap.scaled(target_size[0], target_size[1], Qt.KeepAspectRatio, Qt.SmoothTransformation)
    return pixmap


def parse_page_range(range_text, max_pages):
    """
    Parse teks seperti '1-3,5,8-10' jadi list index halaman (0-based, unik,
    terurut). Mengembalikan None kalau format tidak valid.
    """
    if not range_text.strip():
        return None
    pages = set()
    try:
        for part in range_text.split(','):
            part = part.strip()
            if not part:
                continue
            if '-' in part:
                start_s, end_s = part.split('-', 1)
                start, end = int(start_s), int(end_s)
                if start < 1 or end < start:
                    return None
                for p in range(start, end + 1):
                    if 1 <= p <= max_pages:
                        pages.add(p - 1)
            else:
                p = int(part)
                if 1 <= p <= max_pages:
                    pages.add(p - 1)
    except ValueError:
        return None
    return sorted(pages) if pages else None




class ConverterDropPage(QWidget):
    """Halaman Converter yang menerima file dari Windows Explorer."""

    def __init__(self, parent_window):
        super().__init__(parent_window)
        self.parent_window = parent_window
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        paths = self.parent_window._dropped_paths(event)
        if paths and self.parent_window.handle_converter_drop(paths):
            event.acceptProposedAction()
        else:
            event.ignore()

class EnhancedImageToPDFConverter(QMainWindow):
    def __init__(self):
        super().__init__()
        self.file_paths = []
        self.selected_index = -1
        self.preview_panels = {False: {}, True: {}}
        self.preview_file_path = None

        # State untuk tab-tab baru (single-file tools)
        self.split_pdf_path = None
        self.rotate_pdf_path = None
        self.watermark_pdf_path = None
        self.pdf2jpg_paths = []
        self.ico_paths = []
        self.converter_pending_paths = []
        self.image_cover_selection = 0

        self.setup_ui()

        if not PIL_AVAILABLE:
            QMessageBox.warning(self, "Warning",
                "Pillow library is required for image processing. Please install it using: pip install Pillow")

        if not PYPDF2_AVAILABLE:
            QMessageBox.warning(self, "Warning",
                "PyPDF2 library is required for PDF operations. Please install it using: pip install PyPDF2")

        if not REPORTLAB_AVAILABLE:
            QMessageBox.warning(self, "Warning",
                "reportlab is required for the Watermark tool. Please install it using: pip install reportlab")

        if not FITZ_AVAILABLE:
            QMessageBox.warning(self, "Warning",
                "PyMuPDF is required for PDF to JPG. Please install it using: pip install PyMuPDF")

    def setup_ui(self):
        self.setWindowTitle("PDF & Image Toolbox")
        self.setGeometry(100, 100, 1300, 800)
        self.setAcceptDrops(True)

        font = QFont("Segoe UI", 9)
        QApplication.setFont(font)

        central_widget = QWidget()
        central_widget.setAcceptDrops(True)
        central_widget.setStyleSheet(f"background-color: {OFFWHITE};")
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        self.stacked = QStackedWidget()
        main_layout.addWidget(self.stacked)

        self.tool_stack = QStackedWidget()

        self.image_tab = QWidget()
        self.setup_image_tab()

        self.pdf_tab = QWidget()
        self.setup_pdf_tab()

        self.split_tab = QWidget()
        self.setup_split_tab()

        self.rotate_tab = QWidget()
        self.setup_rotate_tab()

        self.pdf2jpg_tab = QWidget()
        self.setup_pdf2jpg_tab()

        self.ico_tab = QWidget()
        self.setup_ico_tab()

        self.watermark_tab = QWidget()
        self.setup_watermark_tab()
        self.tool_stack.addWidget(self.image_tab)
        self.tool_stack.addWidget(self.pdf_tab)
        self.tool_stack.addWidget(self.split_tab)
        self.tool_stack.addWidget(self.rotate_tab)
        self.tool_stack.addWidget(self.pdf2jpg_tab)
        self.tool_stack.addWidget(self.ico_tab)
        self.tool_stack.addWidget(self.watermark_tab)

        tools_page = QWidget()
        tools_page.setStyleSheet(f"background-color: {OFFWHITE};")
        tools_layout = QVBoxLayout(tools_page)
        tools_layout.setContentsMargins(20, 20, 20, 20)
        tools_layout.setSpacing(15)

        back_row = QHBoxLayout()
        btn_back = QPushButton("← Kembali ke Beranda")
        btn_back.setStyleSheet(BLACK_BUTTON_STYLE)
        btn_back.setCursor(Qt.PointingHandCursor)
        btn_back.clicked.connect(self.go_home)
        back_row.addWidget(btn_back)
        back_row.addStretch()
        tools_layout.addLayout(back_row)

        tools_layout.addWidget(self.tool_stack)

        home_page = self.build_home_page()

        converter_page = self.build_converter_page()

        self.stacked.addWidget(home_page)       # index 0
        self.stacked.addWidget(tools_page)      # index 1
        self.stacked.addWidget(converter_page)  # index 2
        self.stacked.setCurrentIndex(0)

    def go_home(self):
        self.stacked.setCurrentIndex(0)

    def open_tool(self, tab_index):
        self.tool_stack.setCurrentIndex(tab_index)
        self.stacked.setCurrentIndex(1)

    def open_converter_page(self):
        self.stacked.setCurrentIndex(2)

    def show_coming_soon(self, feature_name):
        QMessageBox.information(
            self,
            "Segera Hadir",
            f"Fitur '{feature_name}' belum tersedia di versi ini.\nAkan ditambahkan di update berikutnya."
        )

    def build_home_page(self):
        page = QWidget()
        page.setStyleSheet(f"background-color: {HOME_BG};")
        page_layout = QVBoxLayout(page)
        page_layout.setContentsMargins(30, 30, 30, 20)
        page_layout.setSpacing(20)

        title = QLabel("📄 PDF & Image Toolbox")
        title.setStyleSheet(f"""
            color: {WHITE};
            font-size: 26px;
            font-weight: bold;
        """)
        page_layout.addWidget(title)

        subtitle = QLabel("Pilih salah satu fitur di bawah ini untuk mulai")
        subtitle.setStyleSheet(f"color: {CARD_DESC}; font-size: 14px;")
        page_layout.addWidget(subtitle)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        grid_container = QWidget()
        grid_container.setStyleSheet("background: transparent;")
        grid = QGridLayout(grid_container)
        grid.setSpacing(16)
        grid.setContentsMargins(2, 2, 2, 20)

        # (icon, judul, deskripsi, warna badge, tab_index_kalau_aktif)
        # tab_index None = fitur belum diimplementasikan -> tampil sebagai
        # kartu "Segera Hadir" dan klik-nya cuma kasih info, tidak error.
        # tab_index bisa berupa:
        #   int    -> buka tab tersebut langsung lewat open_tool()
        #   "converter" -> buka halaman pemilih format (Converter, gaya CloudConvert)
        #   None   -> fitur belum diimplementasikan, tampil sebagai "Segera Hadir"
        tools = [
            ("🔀", "Converter", "Ubah file antar format: gambar, PDF, Word, PowerPoint, Excel, dan lainnya - tinggal pilih format asal dan tujuan.", RED, "converter"),
            ("🔗", "Gabungkan PDF", "Gabungkan PDF dengan urutan yang Anda inginkan dengan penggabungan PDF termudah.", RED, 1),
            ("✂️", "Pisahkan PDF", "Pisahkan satu halaman atau semuanya agar mudah dikonversi menjadi file PDF terpisah.", RED, 2),
            ("🗜️", "Kompres PDF", "Kurangi ukuran file dengan tetap mengoptimalkan kualitas PDF maksimal.", "#27ae60", None),
            ("✏️", "Edit PDF", "Tambahkan teks, gambar, bentuk, atau anotasi manual ke dokumen PDF.", "#8e44ad", None),
            ("✍️", "Tanda Tangani PDF", "Tanda tangani oleh Anda sendiri atau minta tanda tangan elektronik.", "#2f6fed", None),
            ("💧", "Tanda Air", "Tempelkan gambar atau teks di atas PDF Anda dalam hitungan detik.", "#8e44ad", 6),
            ("🔄", "Putar PDF", "Putar PDF sesuai kebutuhan, bahkan beberapa PDF sekaligus.", "#8e44ad", 3),
        ]

        cols = 3
        for i, (icon, name, desc, color, tab_index) in enumerate(tools):
            row, col = divmod(i, cols)
            if tab_index == "converter":
                enabled = True
                handler = self.open_converter_page
            elif tab_index is not None:
                enabled = True
                handler = (lambda idx=tab_index: self.open_tool(idx))
            else:
                enabled = False
                handler = (lambda n=name: self.show_coming_soon(n))
            card = ToolCard(icon, name, desc, color, enabled=enabled, on_click=handler)
            grid.addWidget(card, row, col)

        scroll.setWidget(grid_container)
        page_layout.addWidget(scroll)

        return page

    CONVERTER_FORMAT_GROUPS = [
        ("Gambar", "🖼️", [
            ("JPG", "JPG - JPEG Image"),
            ("PNG", "PNG - Portable Network Graphic"),
            ("BMP", "BMP - Bitmap Image"),
            ("GIF", "GIF - Graphics Interchange Format"),
            ("WEBP", "WEBP - WebP Image"),
            ("TIFF", "TIFF - Tagged Image"),
            ("ICO", "ICO - Icon File"),
        ]),
        ("Dokumen", "📄", [
            ("PDF", "PDF - Portable Document Format"),
            ("DOCX", "DOCX - Word Document"),
        ]),
        ("Presentasi", "📊", [
            ("PPTX", "PPTX - PowerPoint Presentation"),
        ]),
        ("Spreadsheet", "📈", [
            ("XLSX", "XLSX - Excel Spreadsheet"),
        ]),
    ]

    CONVERTER_IMAGE_FORMATS = {"JPG", "PNG", "BMP", "GIF", "WEBP", "TIFF", "ICO"}

    CONVERTER_ROUTES = {
        ("IMG", "PDF"): 0,
        ("PDF", "JPG"): 4,
        ("IMG", "ICO"): 5,
    }

    CONVERTER_EXT_TO_FORMAT = {
        "JPG": "JPG", "JPEG": "JPG",
        "PNG": "PNG",
        "BMP": "BMP",
        "GIF": "GIF",
        "WEBP": "WEBP",
        "TIF": "TIFF", "TIFF": "TIFF",
        "ICO": "ICO",
        "PDF": "PDF",
        "DOCX": "DOCX",
        "PPTX": "PPTX",
        "XLSX": "XLSX",
    }

    def _converter_can_handle(self, from_fmt, to_fmt):
        """Cek apakah pasangan format ini benar-benar bisa dikonversi saat ini."""
        if not from_fmt or not to_fmt or from_fmt == to_fmt:
            return False
        img = self.CONVERTER_IMAGE_FORMATS
        if from_fmt in img and to_fmt in img:
            return True
        if from_fmt in img and to_fmt == "PDF":
            return True
        if from_fmt == "PDF" and to_fmt in img:
            return True
        return False

    def build_converter_page(self):
        page = ConverterDropPage(self)
        page.setStyleSheet(f"background-color: {OFFWHITE};")
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        back_row = QHBoxLayout()
        btn_back = QPushButton("← Kembali ke Beranda")
        btn_back.setStyleSheet(BLACK_BUTTON_STYLE)
        btn_back.setCursor(Qt.PointingHandCursor)
        btn_back.clicked.connect(self.go_home)
        back_row.addWidget(btn_back)
        back_row.addStretch()
        layout.addLayout(back_row)

        title_label = QLabel("🔀 Converter")
        title_label.setStyleSheet(TITLE_BANNER_STYLE)
        layout.addWidget(title_label)

        subtitle = QLabel("Pilih format asal dan format tujuan, lalu klik Mulai Convert.")
        subtitle.setStyleSheet(f"color: {MUTED}; font-size: 14px;")
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)

        picker_group = QGroupBox("🔽 Pilih Format")
        picker_group.setStyleSheet(GROUPBOX_STYLE)
        picker_layout = QVBoxLayout(picker_group)
        picker_layout.setSpacing(15)

        boxes_row = QHBoxLayout()
        boxes_row.setSpacing(20)

        self.converter_from_fmt = None
        self.converter_to_fmt = None

        self.btn_converter_from = self._make_format_box_button()
        self.btn_converter_from.clicked.connect(lambda: self._open_format_menu(True))

        btn_swap = QPushButton("⇄")
        btn_swap.setFixedSize(46, 46)
        btn_swap.setCursor(Qt.PointingHandCursor)
        btn_swap.setStyleSheet(f"""
            QPushButton {{
                background: {RED};
                color: {WHITE};
                border-radius: 23px;
                font-size: 18px;
                font-weight: bold;
                border: none;
            }}
            QPushButton:hover {{ background: {RED_DARK}; }}
        """)
        btn_swap.clicked.connect(self._swap_converter_formats)

        self.btn_converter_to = self._make_format_box_button()
        self.btn_converter_to.clicked.connect(lambda: self._open_format_menu(False))

        boxes_row.addWidget(self.btn_converter_from, 1)
        boxes_row.addWidget(btn_swap, 0, Qt.AlignVCenter)
        boxes_row.addWidget(self.btn_converter_to, 1)
        picker_layout.addLayout(boxes_row)

        quick_row = QHBoxLayout()
        quick_row.setSpacing(10)
        quick_label = QLabel("Populer:")
        quick_label.setStyleSheet(f"color: {MUTED}; font-size: 13px;")
        quick_row.addWidget(quick_label)
        for label, from_fmt, to_fmt in [
            ("JPG → PDF", "JPG", "PDF"),
            ("PDF → JPG", "PDF", "JPG"),
            ("Gambar → ICO", "PNG", "ICO"),
        ]:
            chip = QPushButton(label)
            chip.setCursor(Qt.PointingHandCursor)
            chip.setStyleSheet(f"""
                QPushButton {{
                    background: {WHITE};
                    color: {RED_DARK};
                    border: 1px solid {RED};
                    border-radius: 14px;
                    padding: 6px 14px;
                    font-size: 12px;
                    font-weight: bold;
                }}
                QPushButton:hover {{ background: {RED}; color: {WHITE}; }}
            """)
            chip.clicked.connect(lambda checked=False, f=from_fmt, t=to_fmt: self._set_converter_pair(f, t))
            quick_row.addWidget(chip)
        quick_row.addStretch()
        picker_layout.addLayout(quick_row)

        layout.addWidget(picker_group)

        self.btn_start_convert = QPushButton("🔀 Mulai Convert")
        self.btn_start_convert.setStyleSheet(ACTION_BUTTON_STYLE)
        self.btn_start_convert.setCursor(Qt.PointingHandCursor)
        self.btn_start_convert.setEnabled(False)
        self.btn_start_convert.clicked.connect(self._start_converter_flow)
        layout.addWidget(self.btn_start_convert)

        self.converter_status_label = QLabel(
            "📥 Drag & drop file ke halaman ini, atau pilih format secara manual.\n"
            "✅ Didukung saat ini: Gambar → PDF, PDF → JPG, Gambar → ICO.\n"
            "📌 Format lain (Word, PowerPoint, Excel, dll) akan segera hadir."
        )
        self.converter_status_label.setStyleSheet(STATUS_LABEL_STYLE)
        self.converter_status_label.setAlignment(Qt.AlignCenter)
        self.converter_status_label.setWordWrap(True)
        layout.addWidget(self.converter_status_label)

        self._refresh_converter_boxes()

        layout.addStretch()
        return page

    def _make_format_box_button(self):
        btn = QPushButton()
        btn.setCursor(Qt.PointingHandCursor)
        btn.setMinimumHeight(90)
        btn.setStyleSheet(f"""
            QPushButton {{
                background: {WHITE};
                color: {BLACK};
                border: 2px dashed {BORDER};
                border-radius: 10px;
                font-size: 15px;
                font-weight: bold;
                padding: 10px;
                text-align: center;
            }}
            QPushButton:hover {{
                border-color: {RED};
                border-style: solid;
            }}
        """)
        return btn

    def _open_format_menu(self, is_from):
        menu = QMenu(self)
        menu.setStyleSheet(f"""
            QMenu {{ background: {WHITE}; border: 1px solid {BORDER}; padding: 4px; }}
            QMenu::item {{ padding: 6px 24px 6px 12px; color: {BLACK}; }}
            QMenu::item:selected {{ background: {RED}; color: {WHITE}; }}
        """)
        for group_name, emoji, formats in self.CONVERTER_FORMAT_GROUPS:
            submenu = menu.addMenu(f"{emoji}  {group_name}")
            submenu.setStyleSheet(menu.styleSheet())
            for code, label in formats:
                action = submenu.addAction(label)
                action.triggered.connect(
                    lambda checked=False, c=code: self._set_converter_format(is_from, c)
                )
        btn = self.btn_converter_from if is_from else self.btn_converter_to
        menu.exec_(btn.mapToGlobal(QPoint(0, btn.height())))

    def _set_converter_format(self, is_from, fmt_code):
        if is_from:
            self.converter_from_fmt = fmt_code
        else:
            self.converter_to_fmt = fmt_code
        self._refresh_converter_boxes()

    def _set_converter_pair(self, from_fmt, to_fmt):
        self.converter_from_fmt = from_fmt
        self.converter_to_fmt = to_fmt
        self._refresh_converter_boxes()

    def _swap_converter_formats(self):
        self.converter_from_fmt, self.converter_to_fmt = self.converter_to_fmt, self.converter_from_fmt
        self._refresh_converter_boxes()

    def _format_label(self, code):
        if not code:
            return None
        for _, emoji, formats in self.CONVERTER_FORMAT_GROUPS:
            for c, full_label in formats:
                if c == code:
                    return f"{emoji}  {code}\n{full_label}"
        return code

    def _refresh_converter_boxes(self):
        self.btn_converter_from.setText(self._format_label(self.converter_from_fmt) or "➕  Pilih format asal\n▾ klik untuk memilih")
        self.btn_converter_to.setText(self._format_label(self.converter_to_fmt) or "➕  Pilih format tujuan\n▾ klik untuk memilih")

        ready = bool(self.converter_from_fmt) and bool(self.converter_to_fmt) and \
            self.converter_from_fmt != self.converter_to_fmt
        self.btn_start_convert.setEnabled(ready)

    def _resolve_converter_route(self):
        from_fmt = self.converter_from_fmt
        to_fmt = self.converter_to_fmt
        from_key = "IMG" if from_fmt in self.CONVERTER_IMAGE_FORMATS else from_fmt
        return self.CONVERTER_ROUTES.get((from_key, to_fmt))

    def handle_converter_drop(self, paths):
        """Menerima file drag-and-drop dan menyimpannya sebagai input Converter."""
        if not paths:
            return False

        recognized = []
        unsupported = []
        for path in paths:
            ext = os.path.splitext(path)[1].lower().lstrip(".")
            fmt = self.CONVERTER_EXT_TO_FORMAT.get(ext.upper())
            if fmt:
                recognized.append((path, fmt))
            else:
                unsupported.append(path)

        if not recognized:
            QMessageBox.warning(
                self, "Format Tidak Didukung",
                "Tidak ada file yang dikenali oleh Converter."
            )
            return False

        # Converter menggunakan satu format asal untuk satu batch.
        source_formats = {fmt for _, fmt in recognized}
        if len(source_formats) > 1:
            QMessageBox.warning(
                self, "Format Berbeda",
                "Untuk drag & drop beberapa file sekaligus, semua file harus memiliki format asal yang sama."
            )
            return False

        source_fmt = next(iter(source_formats))
        self.converter_from_fmt = source_fmt
        self.converter_pending_paths = [path for path, _ in recognized]

        if hasattr(self, "converter_status_label"):
            count = len(self.converter_pending_paths)
            self.converter_status_label.setText(
                f"📁 {count} file siap dikonversi\n"
                f"Format asal: {source_fmt}\n"
                "Pilih format tujuan, lalu klik Mulai Convert."
            )

        self._refresh_converter_boxes()
        return True

    def _prepare_converter_input(self):
        """Memasukkan file hasil drag-and-drop ke tool tujuan."""
        paths = getattr(self, "converter_pending_paths", [])
        if not paths:
            return True

        from_fmt = self.converter_from_fmt
        to_fmt = self.converter_to_fmt

        if to_fmt == "PDF" and from_fmt in self.CONVERTER_IMAGE_FORMATS:
            for path in paths:
                item = (path, False)
                if item not in self.file_paths:
                    self.file_paths.append(item)
            self.refresh_file_tables()
            self.refresh_image_cover_options()
            self.select_first_row(False)
            if hasattr(self, "status_label_images"):
                self.status_label_images.setText(f"📄 {len([1 for _, is_pdf in self.file_paths if not is_pdf])} gambar dipilih")
            return True

        if from_fmt == "PDF" and to_fmt == "JPG":
            for path in paths:
                if path not in self.pdf2jpg_paths:
                    self.pdf2jpg_paths.append(path)
                    self.pdf2jpg_list.addItem(QListWidgetItem(os.path.basename(path)))
            self.status_label_pdf2jpg.setText(f"📄 {len(self.pdf2jpg_paths)} PDF dipilih")
            return True

        if to_fmt == "ICO" and from_fmt in self.CONVERTER_IMAGE_FORMATS:
            for path in paths:
                if path not in self.ico_paths:
                    self.ico_paths.append(path)
                    self.ico_list.addItem(QListWidgetItem(os.path.basename(path)))
            self.status_label_ico.setText(f"🖼️ {len(self.ico_paths)} gambar dipilih")
            return True

        return False

    def _convert_images_directly(self):
        """Konversi antar-format gambar langsung dari halaman Converter."""
        paths = getattr(self, "converter_pending_paths", [])
        from_fmt = self.converter_from_fmt
        to_fmt = self.converter_to_fmt
        if not paths:
            QMessageBox.warning(self, "Input Tidak Ada", "Silakan drag & drop gambar terlebih dahulu.")
            return
        out_dir = QFileDialog.getExistingDirectory(self, "Pilih Folder Output")
        if not out_dir:
            return
        ext_map = {"JPG":".jpg", "PNG":".png", "BMP":".bmp", "GIF":".gif", "WEBP":".webp", "TIFF":".tiff", "ICO":".ico"}
        converted, errors = 0, []
        for path in paths:
            try:
                with Image.open(path) as source:
                    image = source.convert("RGB") if to_fmt in {"JPG", "BMP"} else source.convert("RGBA") if to_fmt == "ICO" else source.copy()
                    base = os.path.splitext(os.path.basename(path))[0]
                    out_path = os.path.join(out_dir, base + ext_map[to_fmt])
                    n = 1
                    while os.path.exists(out_path):
                        out_path = os.path.join(out_dir, f"{base}_{n}{ext_map[to_fmt]}"); n += 1
                    if to_fmt == "ICO":
                        image.thumbnail((256, 256), Image.LANCZOS if hasattr(Image, "LANCZOS") else Image.Resampling.LANCZOS)
                        image.save(out_path, format="ICO", sizes=[(16,16),(32,32),(48,48),(64,64),(128,128),(256,256)])
                    elif to_fmt == "WEBP":
                        image.save(out_path, format="WEBP", quality=95, method=6)
                    elif to_fmt == "JPG":
                        image.save(out_path, format="JPEG", quality=95, optimize=True)
                    else:
                        image.save(out_path, format=to_fmt)
                    converted += 1
            except Exception as e:
                errors.append(f"{os.path.basename(path)}: {e}")
        if converted:
            msg = f"✅ {converted} file berhasil dikonversi.\n\n{from_fmt} → {to_fmt}\nFolder: {out_dir}"
            if errors: msg += "\n\n❌ Gagal:\n" + "\n".join(errors)
            QMessageBox.information(self, "Konversi Berhasil", msg)
            if hasattr(self, "converter_status_label"):
                self.converter_status_label.setText(f"✅ {converted} file selesai: {from_fmt} → {to_fmt}")
        else:
            QMessageBox.critical(self, "Konversi Gagal", "Tidak ada file yang berhasil dikonversi.\n\n" + "\n".join(errors))

    def _start_converter_flow(self):
        if not self.converter_from_fmt or not self.converter_to_fmt:
            return
        if self.converter_from_fmt == self.converter_to_fmt:
            QMessageBox.warning(self, "Peringatan", "Format asal dan tujuan tidak boleh sama.")
            return
        if self.converter_from_fmt in self.CONVERTER_IMAGE_FORMATS and self.converter_to_fmt in self.CONVERTER_IMAGE_FORMATS:
            self._convert_images_directly()
            return
        tab_index = self._resolve_converter_route()
        if tab_index is None:
            self.show_coming_soon(f"{self.converter_from_fmt} ke {self.converter_to_fmt}")
            return
        if not self._prepare_converter_input():
            QMessageBox.warning(self, "Input Tidak Siap", "File belum dapat diteruskan ke tool konversi.")
            return
        self.open_tool(tab_index)

    # Tab: Image -> PDF

    def setup_image_tab(self):
        layout = QVBoxLayout(self.image_tab)
        layout.setContentsMargins(0, 0, 0, 0)

        splitter = QSplitter(Qt.Horizontal)
        splitter.setChildrenCollapsible(False)
        splitter.setHandleWidth(8)

        left_panel = QWidget()
        left_panel.setMinimumWidth(220)
        left_panel.setMaximumWidth(340)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(15)

        title_label = QLabel("Image ke PDF")
        title_label.setStyleSheet(TITLE_BANNER_STYLE)
        left_layout.addWidget(title_label)

        control_group = QGroupBox("🛠️ Kontrol")
        control_group.setStyleSheet(GROUPBOX_STYLE)
        control_layout = QVBoxLayout(control_group)
        control_layout.setSpacing(10)

        self.btn_select_images = QPushButton("📁 Pilih Gambar")
        self.btn_select_images.clicked.connect(lambda: self.select_files(False))

        self.btn_clear_images = QPushButton("🗑️ Hapus Semua")
        self.btn_clear_images.clicked.connect(self.clear_all)

        for btn in [self.btn_select_images, self.btn_clear_images]:
            btn.setStyleSheet(RED_BUTTON_STYLE)
            control_layout.addWidget(btn)

        instructions = QLabel(
            "• Klik gambar untuk memilih\n"
            "• Drag baris untuk mengurutkan\n"
            "• Klik dua kali baris untuk fokus\n"
            "• Ctrl+Click untuk pilih banyak"
        )
        instructions.setStyleSheet(f"""
            QLabel {{
                color: {MUTED};
                font-size: 13px;
                padding: 12px;
                background-color: {WHITE};
                border-radius: 6px;
                border: 1px solid {BORDER};
            }}
        """)
        instructions.setWordWrap(True)
        control_layout.addWidget(instructions)

        left_layout.addWidget(control_group)

        options_group = QGroupBox("⚙️ Opsi PDF")
        options_group.setStyleSheet(GROUPBOX_STYLE)
        options_layout = QVBoxLayout(options_group)
        options_layout.setSpacing(8)

        options_layout.addWidget(QLabel("Judul PDF:"))
        self.pdf_title = QLineEdit("Combined Images")
        self.pdf_title.setStyleSheet(INPUT_STYLE)
        options_layout.addWidget(self.pdf_title)

        options_layout.addWidget(QLabel("Cover page:"))
        self.cover_image_combo = NoScrollComboBox()
        self.cover_image_combo.setStyleSheet(INPUT_STYLE)
        self.cover_image_combo.addItem("Otomatis (gambar pertama)")
        options_layout.addWidget(self.cover_image_combo)

        options_layout.addWidget(QLabel("Ukuran Halaman:"))
        self.page_size = NoScrollComboBox()
        self.page_size.addItems(["Original", "A4", "Letter", "Legal", "A3", "A5"])
        self.page_size.setStyleSheet(INPUT_STYLE)
        options_layout.addWidget(self.page_size)

        options_layout.addWidget(QLabel("Orientasi:"))
        self.orientation = NoScrollComboBox()
        self.orientation.addItems(["Portrait", "Landscape"])
        self.orientation.setStyleSheet(INPUT_STYLE)
        options_layout.addWidget(self.orientation)

        left_layout.addWidget(options_group)

        self.btn_convert = QPushButton("🔄 Konversi ke PDF")
        self.btn_convert.clicked.connect(self.convert_to_pdf)
        self.btn_convert.setStyleSheet(ACTION_BUTTON_STYLE)
        left_layout.addWidget(self.btn_convert)

        self.status_label_images = QLabel("Pilih gambar untuk mulai")
        self.status_label_images.setStyleSheet(STATUS_LABEL_STYLE)
        self.status_label_images.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(self.status_label_images)

        left_layout.addStretch()
        splitter.addWidget(left_panel)

        detail_panel = self.create_detail_panel(is_pdf=False)
        splitter.addWidget(detail_panel)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)

        layout.addWidget(splitter)

    # Tab: Merge PDFs
    def setup_pdf_tab(self):
        layout = QVBoxLayout(self.pdf_tab)
        layout.setContentsMargins(0, 0, 0, 0)

        splitter = QSplitter(Qt.Horizontal)
        splitter.setChildrenCollapsible(False)
        splitter.setHandleWidth(8)

        left_panel = QWidget()
        left_panel.setMinimumWidth(220)
        left_panel.setMaximumWidth(340)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(15)

        title_label = QLabel("Gabung PDF")
        title_label.setStyleSheet(TITLE_BANNER_STYLE)
        left_layout.addWidget(title_label)

        control_group = QGroupBox("🛠️ Kontrol")
        control_group.setStyleSheet(GROUPBOX_STYLE)
        control_layout = QVBoxLayout(control_group)
        control_layout.setSpacing(10)

        self.btn_select_pdfs = QPushButton("📁 Pilih PDF")
        self.btn_select_pdfs.clicked.connect(lambda: self.select_files(True))

        self.btn_clear_pdfs = QPushButton("🗑️ Hapus Semua")
        self.btn_clear_pdfs.clicked.connect(self.clear_all_pdfs)

        for btn in [self.btn_select_pdfs, self.btn_clear_pdfs]:
            btn.setStyleSheet(RED_BUTTON_STYLE)
            control_layout.addWidget(btn)

        instructions = QLabel(
            "• Klik PDF untuk memilih\n"
            "• Drag baris untuk mengurutkan\n"
            "• Klik dua kali baris untuk fokus\n"
            "• Ctrl+Click untuk pilih banyak"
        )
        instructions.setStyleSheet(f"""
            QLabel {{
                color: {MUTED};
                font-size: 13px;
                padding: 12px;
                background-color: {WHITE};
                border-radius: 6px;
                border: 1px solid {BORDER};
            }}
        """)
        instructions.setWordWrap(True)
        control_layout.addWidget(instructions)

        left_layout.addWidget(control_group)

        self.btn_merge = QPushButton("🔗 Gabungkan PDF")
        self.btn_merge.clicked.connect(self.merge_pdfs)
        self.btn_merge.setStyleSheet(ACTION_BUTTON_STYLE)
        left_layout.addWidget(self.btn_merge)

        self.status_label_pdfs = QLabel("Pilih PDF untuk mulai")
        self.status_label_pdfs.setStyleSheet(STATUS_LABEL_STYLE)
        self.status_label_pdfs.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(self.status_label_pdfs)

        left_layout.addStretch()
        splitter.addWidget(left_panel)

        detail_panel = self.create_detail_panel(is_pdf=True)
        splitter.addWidget(detail_panel)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)

        layout.addWidget(splitter)

    def create_detail_panel(self, is_pdf):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setSpacing(12)
        layout.setContentsMargins(0, 0, 0, 0)

        header = QLabel("📎 File PDF" if is_pdf else "🖼️ File Gambar")
        header.setStyleSheet(HEADER_LABEL_STYLE)
        header.setAlignment(Qt.AlignCenter)
        header.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addWidget(header)

        container = QSplitter(Qt.Horizontal)
        container.setChildrenCollapsible(False)
        container.setHandleWidth(8)

        self.detail_table_images = ReorderableFileTable(self, False) if not is_pdf else getattr(self, 'detail_table_images', None)
        self.detail_table_pdfs = ReorderableFileTable(self, True) if is_pdf else getattr(self, 'detail_table_pdfs', None)
        table = self.detail_table_pdfs if is_pdf else self.detail_table_images
        if table is None:
            table = ReorderableFileTable(self, is_pdf)
            if is_pdf:
                self.detail_table_pdfs = table
            else:
                self.detail_table_images = table

        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["No", "File", "Info", "Preview"])
        table.verticalHeader().setVisible(False)
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.setSelectionMode(QAbstractItemView.SingleSelection)
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setAlternatingRowColors(True)
        table.setShowGrid(False)
        table.setDragDropMode(QAbstractItemView.InternalMove)
        table.setDragEnabled(True)
        table.setAcceptDrops(True)
        table.setDropIndicatorShown(True)
        table.setDefaultDropAction(Qt.MoveAction)
        table.setDragDropOverwriteMode(False)
        table.setFocusPolicy(Qt.StrongFocus)
        table.setStyleSheet(TABLE_STYLE)
        header_view = table.horizontalHeader()
        header_view.setStretchLastSection(False)
        header_view.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header_view.setSectionResizeMode(1, QHeaderView.Stretch)
        header_view.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header_view.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        table.setMinimumWidth(520)
        table.itemSelectionChanged.connect(lambda: self.on_table_selection_changed(is_pdf))
        table.cellDoubleClicked.connect(lambda row, column: self.on_table_double_clicked(is_pdf, row, column))
        table_container = QFrame()
        table_container_layout = QVBoxLayout(table_container)
        table_container_layout.setContentsMargins(0, 0, 0, 0)
        table_container_layout.addWidget(table)
        container.addWidget(table_container)

        preview_panel = QFrame()
        preview_panel.setMinimumWidth(220)
        preview_panel.setStyleSheet(f"""
            QFrame {{
                border: 1px solid {BORDER};
                border-radius: 8px;
                background: {WHITE};
            }}
        """)
        preview_layout = QVBoxLayout(preview_panel)
        preview_layout.setContentsMargins(12, 12, 12, 12)
        preview_layout.setSpacing(10)

        preview_title = QLabel("Preview")
        preview_title.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {BLACK};")
        preview_layout.addWidget(preview_title)

        preview_image_label = QLabel("Pilih sebuah file")
        preview_image_label.setAlignment(Qt.AlignCenter)
        preview_image_label.setMinimumHeight(220)
        preview_image_label.setStyleSheet(f"""
            QLabel {{
                background: {OFFWHITE};
                border: 1px solid {BORDER};
                border-radius: 6px;
                color: {MUTED};
                font-size: 14px;
            }}
        """)
        preview_layout.addWidget(preview_image_label)

        preview_file_label = QLabel("Belum ada file dipilih")
        preview_file_label.setWordWrap(True)
        preview_file_label.setStyleSheet(f"font-weight: bold; color: {BLACK}; font-size: 14px;")
        preview_layout.addWidget(preview_file_label)

        preview_info_label = QLabel("")
        preview_info_label.setWordWrap(True)
        preview_info_label.setStyleSheet(f"color: {MUTED}; font-size: 13px;")
        preview_layout.addWidget(preview_info_label)

        preview_meta_label = QLabel("")
        preview_meta_label.setWordWrap(True)
        preview_meta_label.setStyleSheet(f"color: {MUTED}; font-size: 12px;")
        preview_layout.addWidget(preview_meta_label)

        preview_layout.addStretch()
        container.addWidget(preview_panel)
        container.setStretchFactor(0, 1)
        container.setStretchFactor(1, 0)

        layout.addWidget(container, 1)

        self.preview_panels[is_pdf] = {
            'image': preview_image_label,
            'file': preview_file_label,
            'info': preview_info_label,
            'meta': preview_meta_label,
        }

        return panel

    # Tab: Split PDF

    def setup_split_tab(self):
        layout = QVBoxLayout(self.split_tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        title_label = QLabel("Pisahkan PDF")
        title_label.setStyleSheet(TITLE_BANNER_STYLE)
        layout.addWidget(title_label)

        row = QHBoxLayout()
        self.btn_select_split_pdf = QPushButton("📁 Pilih PDF")
        self.btn_select_split_pdf.setStyleSheet(RED_BUTTON_STYLE)
        self.btn_select_split_pdf.clicked.connect(self.select_split_pdf)
        row.addWidget(self.btn_select_split_pdf)

        self.split_pdf_label = QLabel("Belum ada PDF dipilih")
        self.split_pdf_label.setStyleSheet(STATUS_LABEL_STYLE)
        row.addWidget(self.split_pdf_label, 1)
        layout.addLayout(row)

        options_group = QGroupBox("⚙️ Opsi Pemisahan")
        options_group.setStyleSheet(GROUPBOX_STYLE)
        options_layout = QVBoxLayout(options_group)
        options_layout.setSpacing(10)

        self.split_mode_group = QButtonGroup(self)
        self.radio_split_all = QRadioButton("Pisahkan setiap halaman menjadi file terpisah")
        self.radio_split_range = QRadioButton("Ekstrak halaman tertentu ke satu file PDF baru")
        self.radio_split_all.setChecked(True)
        self.split_mode_group.addButton(self.radio_split_all)
        self.split_mode_group.addButton(self.radio_split_range)
        for rb in (self.radio_split_all, self.radio_split_range):
            rb.setStyleSheet(f"font-size: 14px; color: {BLACK};")
            options_layout.addWidget(rb)

        range_row = QHBoxLayout()
        range_row.addWidget(QLabel("Rentang halaman (contoh: 1-3,5,8-10):"))
        self.split_range_input = QLineEdit()
        self.split_range_input.setPlaceholderText("mis. 1-3,5")
        self.split_range_input.setStyleSheet(INPUT_STYLE)
        range_row.addWidget(self.split_range_input, 1)
        options_layout.addLayout(range_row)

        layout.addWidget(options_group)

        self.btn_do_split = QPushButton("✂️ Pisahkan PDF")
        self.btn_do_split.setStyleSheet(ACTION_BUTTON_STYLE)
        self.btn_do_split.clicked.connect(self.split_pdf_action)
        layout.addWidget(self.btn_do_split)

        self.status_label_split = QLabel("Pilih PDF untuk mulai")
        self.status_label_split.setStyleSheet(STATUS_LABEL_STYLE)
        self.status_label_split.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label_split)

        layout.addStretch()

    def select_split_pdf(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Pilih PDF", "", "PDF Files (*.pdf);;All Files (*)")
        if file_path:
            self.split_pdf_path = file_path
            self.split_pdf_label.setText(os.path.basename(file_path))

    def split_pdf_action(self):
        if not PYPDF2_AVAILABLE:
            QMessageBox.critical(self, "Error", "PyPDF2 tidak tersedia. Install dulu: pip install PyPDF2")
            return
        if not self.split_pdf_path:
            QMessageBox.warning(self, "Peringatan", "Pilih file PDF terlebih dahulu")
            return

        try:
            reader = PdfReader(self.split_pdf_path)
            total_pages = len(reader.pages)
            base_name = os.path.splitext(os.path.basename(self.split_pdf_path))[0]

            if self.radio_split_all.isChecked():
                out_dir = QFileDialog.getExistingDirectory(self, "Pilih Folder Output")
                if not out_dir:
                    return
                for i in range(total_pages):
                    writer = PdfWriter()
                    writer.add_page(reader.pages[i])
                    out_path = os.path.join(out_dir, f"{base_name}_hal_{i + 1}.pdf")
                    with open(out_path, "wb") as f:
                        writer.write(f)
                self.status_label_split.setText(f"✅ {total_pages} file berhasil dibuat di {out_dir}")
                QMessageBox.information(self, "Berhasil", f"✅ {total_pages} halaman berhasil dipisahkan")
            else:
                page_indices = parse_page_range(self.split_range_input.text(), total_pages)
                if not page_indices:
                    QMessageBox.warning(self, "Peringatan", "Rentang halaman tidak valid")
                    return
                save_path, _ = QFileDialog.getSaveFileName(self, "Simpan PDF Sebagai", "", "PDF Files (*.pdf)")
                if not save_path:
                    return
                if not save_path.lower().endswith('.pdf'):
                    save_path += '.pdf'
                writer = PdfWriter()
                for idx in page_indices:
                    writer.add_page(reader.pages[idx])
                with open(save_path, "wb") as f:
                    writer.write(f)
                self.status_label_split.setText(f"✅ {len(page_indices)} halaman disimpan ke {os.path.basename(save_path)}")
                QMessageBox.information(self, "Berhasil", "✅ PDF berhasil diekstrak")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"❌ Terjadi kesalahan: {str(e)}")

    # Tab: Rotate PDF
    def setup_rotate_tab(self):
        layout = QVBoxLayout(self.rotate_tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        title_label = QLabel("Putar PDF")
        title_label.setStyleSheet(TITLE_BANNER_STYLE)
        layout.addWidget(title_label)

        row = QHBoxLayout()
        self.btn_select_rotate_pdf = QPushButton("📁 Pilih PDF")
        self.btn_select_rotate_pdf.setStyleSheet(RED_BUTTON_STYLE)
        self.btn_select_rotate_pdf.clicked.connect(self.select_rotate_pdf)
        row.addWidget(self.btn_select_rotate_pdf)

        self.rotate_pdf_label = QLabel("Belum ada PDF dipilih")
        self.rotate_pdf_label.setStyleSheet(STATUS_LABEL_STYLE)
        row.addWidget(self.rotate_pdf_label, 1)
        layout.addLayout(row)

        options_group = QGroupBox("⚙️ Opsi Rotasi")
        options_group.setStyleSheet(GROUPBOX_STYLE)
        options_layout = QVBoxLayout(options_group)
        options_layout.setSpacing(10)

        options_layout.addWidget(QLabel("Sudut Putar:"))
        self.rotate_angle = NoScrollComboBox()
        self.rotate_angle.addItems(["90° (Searah Jarum Jam)", "180°", "270° (Berlawanan Jarum Jam)"])
        self.rotate_angle.setStyleSheet(INPUT_STYLE)
        options_layout.addWidget(self.rotate_angle)

        self.rotate_scope_group = QButtonGroup(self)
        self.radio_rotate_all = QRadioButton("Putar semua halaman")
        self.radio_rotate_specific = QRadioButton("Putar halaman tertentu saja")
        self.radio_rotate_all.setChecked(True)
        self.rotate_scope_group.addButton(self.radio_rotate_all)
        self.rotate_scope_group.addButton(self.radio_rotate_specific)
        for rb in (self.radio_rotate_all, self.radio_rotate_specific):
            rb.setStyleSheet(f"font-size: 14px; color: {BLACK};")
            options_layout.addWidget(rb)

        range_row = QHBoxLayout()
        range_row.addWidget(QLabel("Nomor halaman (contoh: 1-3,5):"))
        self.rotate_range_input = QLineEdit()
        self.rotate_range_input.setPlaceholderText("mis. 1-3,5")
        self.rotate_range_input.setStyleSheet(INPUT_STYLE)
        range_row.addWidget(self.rotate_range_input, 1)
        options_layout.addLayout(range_row)

        layout.addWidget(options_group)

        self.btn_do_rotate = QPushButton("🔄 Putar & Simpan Sebagai")
        self.btn_do_rotate.setStyleSheet(ACTION_BUTTON_STYLE)
        self.btn_do_rotate.clicked.connect(self.rotate_pdf_action)
        layout.addWidget(self.btn_do_rotate)

        self.status_label_rotate = QLabel("Pilih PDF untuk mulai")
        self.status_label_rotate.setStyleSheet(STATUS_LABEL_STYLE)
        self.status_label_rotate.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label_rotate)

        layout.addStretch()

    def select_rotate_pdf(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Pilih PDF", "", "PDF Files (*.pdf);;All Files (*)")
        if file_path:
            self.rotate_pdf_path = file_path
            self.rotate_pdf_label.setText(os.path.basename(file_path))

    def rotate_pdf_action(self):
        if not PYPDF2_AVAILABLE:
            QMessageBox.critical(self, "Error", "PyPDF2 tidak tersedia. Install dulu: pip install PyPDF2")
            return
        if not self.rotate_pdf_path:
            QMessageBox.warning(self, "Peringatan", "Pilih file PDF terlebih dahulu")
            return

        angle_map = {0: 90, 1: 180, 2: 270}
        angle = angle_map[self.rotate_angle.currentIndex()]

        try:
            reader = PdfReader(self.rotate_pdf_path)
            total_pages = len(reader.pages)
            writer = PdfWriter()

            if self.radio_rotate_all.isChecked():
                target_indices = set(range(total_pages))
            else:
                indices = parse_page_range(self.rotate_range_input.text(), total_pages)
                if not indices:
                    QMessageBox.warning(self, "Peringatan", "Nomor halaman tidak valid")
                    return
                target_indices = set(indices)

            for i, page in enumerate(reader.pages):
                if i in target_indices:
                    if hasattr(page, "rotate"):
                        page.rotate(angle)
                    else:
                        page.rotate_clockwise(angle)
                writer.add_page(page)

            save_path, _ = QFileDialog.getSaveFileName(self, "Simpan PDF Sebagai", "", "PDF Files (*.pdf)")
            if not save_path:
                return
            if not save_path.lower().endswith('.pdf'):
                save_path += '.pdf'
            with open(save_path, "wb") as f:
                writer.write(f)

            self.status_label_rotate.setText(f"✅ Disimpan ke {os.path.basename(save_path)}")
            QMessageBox.information(self, "Berhasil", "✅ PDF berhasil diputar")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"❌ Terjadi kesalahan: {str(e)}")

    # Tab: PDF -> JPG

    def setup_pdf2jpg_tab(self):
        layout = QVBoxLayout(self.pdf2jpg_tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        title_label = QLabel("PDF ke JPG")
        title_label.setStyleSheet(TITLE_BANNER_STYLE)
        layout.addWidget(title_label)

        row = QHBoxLayout()
        self.btn_select_pdf2jpg = QPushButton("📁 Pilih PDF")
        self.btn_select_pdf2jpg.setStyleSheet(RED_BUTTON_STYLE)
        self.btn_select_pdf2jpg.clicked.connect(self.select_pdf2jpg_files)
        row.addWidget(self.btn_select_pdf2jpg)

        self.btn_clear_pdf2jpg = QPushButton("🗑️ Hapus Semua")
        self.btn_clear_pdf2jpg.setStyleSheet(RED_BUTTON_STYLE)
        self.btn_clear_pdf2jpg.clicked.connect(self.clear_pdf2jpg_files)
        row.addWidget(self.btn_clear_pdf2jpg)
        layout.addLayout(row)

        self.pdf2jpg_list = QListWidget()
        self.pdf2jpg_list.setStyleSheet(LIST_STYLE)
        self.pdf2jpg_list.setAlternatingRowColors(True)
        layout.addWidget(self.pdf2jpg_list, 1)

        options_group = QGroupBox("⚙️ Opsi Ekspor")
        options_group.setStyleSheet(GROUPBOX_STYLE)
        options_layout = QVBoxLayout(options_group)
        options_layout.addWidget(QLabel("Kualitas / Skala render:"))
        self.pdf2jpg_scale = NoScrollComboBox()
        self.pdf2jpg_scale.addItems(["Standar (150 DPI)", "Tinggi (300 DPI)", "Maksimal (600 DPI)"])
        self.pdf2jpg_scale.setStyleSheet(INPUT_STYLE)
        options_layout.addWidget(self.pdf2jpg_scale)
        layout.addWidget(options_group)

        self.btn_do_pdf2jpg = QPushButton("📤 Konversi ke JPG")
        self.btn_do_pdf2jpg.setStyleSheet(ACTION_BUTTON_STYLE)
        self.btn_do_pdf2jpg.clicked.connect(self.pdf2jpg_action)
        layout.addWidget(self.btn_do_pdf2jpg)

        self.status_label_pdf2jpg = QLabel("Pilih satu atau beberapa PDF untuk mulai")
        self.status_label_pdf2jpg.setStyleSheet(STATUS_LABEL_STYLE)
        self.status_label_pdf2jpg.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label_pdf2jpg)

    # Tab: Image -> ICO
    def setup_ico_tab(self):
        layout = QVBoxLayout(self.ico_tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        title_label = QLabel("Gambar ke ICO")
        title_label.setStyleSheet(TITLE_BANNER_STYLE)
        layout.addWidget(title_label)

        row = QHBoxLayout()
        self.btn_select_ico = QPushButton("📁 Pilih Gambar")
        self.btn_select_ico.setStyleSheet(RED_BUTTON_STYLE)
        self.btn_select_ico.clicked.connect(self.select_ico_files)
        row.addWidget(self.btn_select_ico)

        self.btn_clear_ico = QPushButton("🗑️ Hapus Semua")
        self.btn_clear_ico.setStyleSheet(RED_BUTTON_STYLE)
        self.btn_clear_ico.clicked.connect(self.clear_ico_files)
        row.addWidget(self.btn_clear_ico)
        layout.addLayout(row)

        self.ico_list = QListWidget()
        self.ico_list.setStyleSheet(LIST_STYLE)
        self.ico_list.setAlternatingRowColors(True)
        layout.addWidget(self.ico_list, 1)

        options_group = QGroupBox("⚙️ Opsi ICO")
        options_group.setStyleSheet(GROUPBOX_STYLE)
        options_layout = QVBoxLayout(options_group)
        options_layout.setSpacing(10)

        options_layout.addWidget(QLabel("Mode ukuran icon:"))
        self.ico_size_mode = NoScrollComboBox()
        self.ico_size_mode.addItems([
            "Pertahankan resolusi asli (detail maksimal)",
            "Standar icon 256x256",
        ])
        self.ico_size_mode.setStyleSheet(INPUT_STYLE)
        options_layout.addWidget(self.ico_size_mode)

        hint_label = QLabel(
            "ICO akan dibuat sebagai icon multi-ukuran agar hasil lebih tajam. "
            "Kalau gambar sumber sangat sederhana, ukuran file tetap bisa kecil."
        )
        hint_label.setWordWrap(True)
        hint_label.setStyleSheet(f"color: {MUTED}; font-size: 12px;")
        options_layout.addWidget(hint_label)

        layout.addWidget(options_group)

        self.btn_do_ico = QPushButton("🖼️ Konversi ke ICO")
        self.btn_do_ico.setStyleSheet(ACTION_BUTTON_STYLE)
        self.btn_do_ico.clicked.connect(self.ico_action)
        layout.addWidget(self.btn_do_ico)

        self.status_label_ico = QLabel("Pilih satu atau beberapa gambar untuk mulai")
        self.status_label_ico.setStyleSheet(STATUS_LABEL_STYLE)
        self.status_label_ico.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label_ico)

    def select_ico_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Pilih Gambar",
            "",
            "Image Files (*.png *.jpg *.jpeg *.bmp *.tiff *.webp *.gif);;All Files (*)"
        )
        if files:
            for file_path in files:
                if file_path not in self.ico_paths:
                    self.ico_paths.append(file_path)
                    self.ico_list.addItem(QListWidgetItem(os.path.basename(file_path)))
            self.status_label_ico.setText(f"🖼️ {len(self.ico_paths)} gambar dipilih")

    def clear_ico_files(self):
        self.ico_paths = []
        self.ico_list.clear()
        self.status_label_ico.setText("Pilih satu atau beberapa gambar untuk mulai")

    def _create_ico_canvas(self, image, canvas_size):
        canvas = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
        if image.width == 0 or image.height == 0:
            return canvas

        scale = min(canvas_size / image.width, canvas_size / image.height)
        target_width = max(1, int(round(image.width * scale)))
        target_height = max(1, int(round(image.height * scale)))
        resample = Image.LANCZOS if hasattr(Image, "LANCZOS") else Image.ANTIALIAS
        resized = image.resize((target_width, target_height), resample)
        offset_x = (canvas_size - target_width) // 2
        offset_y = (canvas_size - target_height) // 2
        canvas.paste(resized, (offset_x, offset_y), resized if resized.mode == "RGBA" else None)
        return canvas

    def _build_ico_sizes(self, source_size, preserve_original):
        width, height = source_size
        max_side = max(width, height)
        if not preserve_original:
            max_side = min(max_side, 256)

        candidates = [max_side, 256, 128, 64, 48, 32, 24, 16]
        sizes = []
        for size in candidates:
            if size <= 0:
                continue
            if size <= max_side and size not in sizes:
                sizes.append(size)

        if not sizes:
            sizes = [16]
        return [(size, size) for size in sizes]

    def ico_action(self):
        if not PIL_AVAILABLE:
            QMessageBox.critical(self, "Error", "Pillow library is not available. Please install it first.")
            return
        if not self.ico_paths:
            QMessageBox.warning(self, "Peringatan", "Pilih gambar terlebih dahulu")
            return

        out_dir = QFileDialog.getExistingDirectory(self, "Pilih Folder Output")
        if not out_dir:
            return

        preserve_original = self.ico_size_mode.currentIndex() == 0

        try:
            converted_count = 0
            for image_path in self.ico_paths:
                with Image.open(image_path) as source_image:
                    image = source_image.convert("RGBA")
                    sizes = self._build_ico_sizes(image.size, preserve_original)
                    largest_size = sizes[0][0]
                    ico_base = self._create_ico_canvas(image, largest_size)

                    base_name = os.path.splitext(os.path.basename(image_path))[0]
                    out_path = os.path.join(out_dir, f"{base_name}.ico")
                    ico_base.save(out_path, format="ICO", sizes=sizes)

                    converted_count += 1

            self.status_label_ico.setText(f"✅ {converted_count} file ICO disimpan di {out_dir}")
            QMessageBox.information(self, "Berhasil", f"✅ {converted_count} gambar berhasil dikonversi ke ICO")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"❌ Terjadi kesalahan: {str(e)}")

    def select_pdf2jpg_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Pilih PDF", "", "PDF Files (*.pdf);;All Files (*)")
        if files:
            for f in files:
                if f not in self.pdf2jpg_paths:
                    self.pdf2jpg_paths.append(f)
                    self.pdf2jpg_list.addItem(QListWidgetItem(os.path.basename(f)))
            self.status_label_pdf2jpg.setText(f"📄 {len(self.pdf2jpg_paths)} PDF dipilih")

    def clear_pdf2jpg_files(self):
        self.pdf2jpg_paths = []
        self.pdf2jpg_list.clear()
        self.status_label_pdf2jpg.setText("Pilih satu atau beberapa PDF untuk mulai")

    def pdf2jpg_action(self):
        if not FITZ_AVAILABLE:
            QMessageBox.critical(self, "Error", "PyMuPDF tidak tersedia. Install dulu: pip install PyMuPDF")
            return
        if not self.pdf2jpg_paths:
            QMessageBox.warning(self, "Peringatan", "Pilih file PDF terlebih dahulu")
            return

        dpi_map = {0: 150, 1: 300, 2: 600}
        dpi = dpi_map[self.pdf2jpg_scale.currentIndex()]
        zoom = dpi / 72.0

        out_dir = QFileDialog.getExistingDirectory(self, "Pilih Folder Output")
        if not out_dir:
            return

        try:
            total_images = 0
            for pdf_path in self.pdf2jpg_paths:
                base_name = os.path.splitext(os.path.basename(pdf_path))[0]
                doc = fitz.open(pdf_path)
                matrix = fitz.Matrix(zoom, zoom)
                for page_num in range(len(doc)):
                    page = doc.load_page(page_num)
                    pix = page.get_pixmap(matrix=matrix)
                    out_path = os.path.join(out_dir, f"{base_name}_hal_{page_num + 1}.jpg")
                    pix.save(out_path)
                    total_images += 1
                doc.close()

            self.status_label_pdf2jpg.setText(f"✅ {total_images} gambar disimpan di {out_dir}")
            QMessageBox.information(self, "Berhasil", f"✅ {total_images} halaman berhasil diekspor ke JPG")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"❌ Terjadi kesalahan: {str(e)}")

    def _dropped_paths(self, event):
        paths = []
        if not event.mimeData().hasUrls():
            return paths
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if file_path and os.path.isfile(file_path):
                paths.append(file_path)
        return paths

    def _filter_dropped_files(self, paths, allowed_exts):
        return [path for path in paths if path.lower().endswith(allowed_exts)]

    def _set_single_pdf_target(self, file_path, label_widget, attr_name, status_widget, status_text):
        setattr(self, attr_name, file_path)
        label_widget.setText(os.path.basename(file_path))
        status_widget.setText(status_text)

    def _handle_dropped_files(self, paths):
        current_tool = self.tool_stack.currentIndex()

        if current_tool == 0:
            image_files = self._filter_dropped_files(paths, SUPPORTED_IMAGE_EXTS)
            if not image_files:
                return False
            self.add_files_from_paths([(path, False) for path in image_files])
            image_count = sum(1 for _, file_is_pdf in self.file_paths if not file_is_pdf)
            self.status_label_images.setText(f"📄 {image_count} gambar dipilih" if image_count else "Pilih gambar untuk mulai")
            return True

        if current_tool == 1:
            pdf_files = self._filter_dropped_files(paths, SUPPORTED_PDF_EXTS)
            if not pdf_files:
                return False
            self.add_files_from_paths([(path, True) for path in pdf_files])
            pdf_count = sum(1 for _, file_is_pdf in self.file_paths if file_is_pdf)
            self.status_label_pdfs.setText(f"📄 {pdf_count} PDF dipilih" if pdf_count else "Pilih PDF untuk mulai")
            return True

        if current_tool == 2:
            pdf_files = self._filter_dropped_files(paths, SUPPORTED_PDF_EXTS)
            if not pdf_files:
                return False
            self._set_single_pdf_target(
                pdf_files[0],
                self.split_pdf_label,
                'split_pdf_path',
                self.status_label_split,
                f"📄 {os.path.basename(pdf_files[0])} siap dipisahkan"
            )
            return True

        if current_tool == 3:
            pdf_files = self._filter_dropped_files(paths, SUPPORTED_PDF_EXTS)
            if not pdf_files:
                return False
            self._set_single_pdf_target(
                pdf_files[0],
                self.rotate_pdf_label,
                'rotate_pdf_path',
                self.status_label_rotate,
                f"📄 {os.path.basename(pdf_files[0])} siap diputar"
            )
            return True

        if current_tool == 4:
            pdf_files = self._filter_dropped_files(paths, SUPPORTED_PDF_EXTS)
            if not pdf_files:
                return False
            for pdf_path in pdf_files:
                if pdf_path not in self.pdf2jpg_paths:
                    self.pdf2jpg_paths.append(pdf_path)
                    self.pdf2jpg_list.addItem(QListWidgetItem(os.path.basename(pdf_path)))
            self.status_label_pdf2jpg.setText(f"📄 {len(self.pdf2jpg_paths)} PDF dipilih")
            return True

        if current_tool == 5:
            image_files = self._filter_dropped_files(paths, SUPPORTED_IMAGE_EXTS)
            if not image_files:
                return False
            for image_path in image_files:
                if image_path not in self.ico_paths:
                    self.ico_paths.append(image_path)
                    self.ico_list.addItem(QListWidgetItem(os.path.basename(image_path)))
            self.status_label_ico.setText(f"🖼️ {len(self.ico_paths)} gambar dipilih")
            return True

        if current_tool == 6:
            pdf_files = self._filter_dropped_files(paths, SUPPORTED_PDF_EXTS)
            if not pdf_files:
                return False
            self._set_single_pdf_target(
                pdf_files[0],
                self.watermark_pdf_label,
                'watermark_pdf_path',
                self.status_label_watermark,
                f"📄 {os.path.basename(pdf_files[0])} siap diberi tanda air"
            )
            return True

        return False

    # Tab: Watermark
    def setup_watermark_tab(self):
        layout = QVBoxLayout(self.watermark_tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        title_label = QLabel("Tanda Air (Watermark)")
        title_label.setStyleSheet(TITLE_BANNER_STYLE)
        layout.addWidget(title_label)

        row = QHBoxLayout()
        self.btn_select_watermark_pdf = QPushButton("📁 Pilih PDF")
        self.btn_select_watermark_pdf.setStyleSheet(RED_BUTTON_STYLE)
        self.btn_select_watermark_pdf.clicked.connect(self.select_watermark_pdf)
        row.addWidget(self.btn_select_watermark_pdf)

        self.watermark_pdf_label = QLabel("Belum ada PDF dipilih")
        self.watermark_pdf_label.setStyleSheet(STATUS_LABEL_STYLE)
        row.addWidget(self.watermark_pdf_label, 1)
        layout.addLayout(row)

        options_group = QGroupBox("⚙️ Opsi Tanda Air")
        options_group.setStyleSheet(GROUPBOX_STYLE)
        options_layout = QVBoxLayout(options_group)
        options_layout.setSpacing(10)

        options_layout.addWidget(QLabel("Teks Tanda Air:"))
        self.watermark_text = QLineEdit("CONFIDENTIAL")
        self.watermark_text.setStyleSheet(INPUT_STYLE)
        options_layout.addWidget(self.watermark_text)

        size_row = QHBoxLayout()
        size_row.addWidget(QLabel("Ukuran Font:"))
        self.watermark_font_size = QSpinBox()
        self.watermark_font_size.setRange(10, 200)
        self.watermark_font_size.setValue(50)
        self.watermark_font_size.setStyleSheet(INPUT_STYLE)
        size_row.addWidget(self.watermark_font_size)
        options_layout.addLayout(size_row)

        opacity_row = QHBoxLayout()
        opacity_row.addWidget(QLabel("Transparansi:"))
        self.watermark_opacity = QSlider(Qt.Horizontal)
        self.watermark_opacity.setRange(10, 100)
        self.watermark_opacity.setValue(30)
        opacity_row.addWidget(self.watermark_opacity, 1)
        options_layout.addLayout(opacity_row)

        options_layout.addWidget(QLabel("Posisi:"))
        self.watermark_position = NoScrollComboBox()
        self.watermark_position.addItems(["Diagonal (Tengah)", "Tengah (Horizontal)"])
        self.watermark_position.setStyleSheet(INPUT_STYLE)
        options_layout.addWidget(self.watermark_position)

        layout.addWidget(options_group)

        self.btn_do_watermark = QPushButton("💧 Terapkan & Simpan Sebagai")
        self.btn_do_watermark.setStyleSheet(ACTION_BUTTON_STYLE)
        self.btn_do_watermark.clicked.connect(self.watermark_pdf_action)
        layout.addWidget(self.btn_do_watermark)

        self.status_label_watermark = QLabel("Pilih PDF untuk mulai")
        self.status_label_watermark.setStyleSheet(STATUS_LABEL_STYLE)
        self.status_label_watermark.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label_watermark)

        layout.addStretch()

    def select_watermark_pdf(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Pilih PDF", "", "PDF Files (*.pdf);;All Files (*)")
        if file_path:
            self.watermark_pdf_path = file_path
            self.watermark_pdf_label.setText(os.path.basename(file_path))

    def _build_watermark_page(self, page_width, page_height):
        """Buat 1 halaman PDF transparan berisi teks watermark, seukuran halaman target."""
        buffer = BytesIO()
        c = rl_canvas.Canvas(buffer, pagesize=(page_width, page_height))

        text = self.watermark_text.text() or "WATERMARK"
        font_size = self.watermark_font_size.value()
        opacity = self.watermark_opacity.value() / 100.0

        c.setFont("Helvetica-Bold", font_size)
        c.setFillColor(Color(0.75, 0, 0, alpha=opacity))  # merah transparan, sesuai tema

        c.saveState()
        c.translate(page_width / 2, page_height / 2)
        if self.watermark_position.currentIndex() == 0:
            c.rotate(45)
        c.drawCentredString(0, 0, text)
        c.restoreState()

        c.save()
        buffer.seek(0)
        return PdfReader(buffer).pages[0]

    def watermark_pdf_action(self):
        if not PYPDF2_AVAILABLE:
            QMessageBox.critical(self, "Error", "PyPDF2 tidak tersedia. Install dulu: pip install PyPDF2")
            return
        if not REPORTLAB_AVAILABLE:
            QMessageBox.critical(self, "Error", "reportlab tidak tersedia. Install dulu: pip install reportlab")
            return
        if not self.watermark_pdf_path:
            QMessageBox.warning(self, "Peringatan", "Pilih file PDF terlebih dahulu")
            return
        if not self.watermark_text.text().strip():
            QMessageBox.warning(self, "Peringatan", "Isi teks tanda air terlebih dahulu")
            return

        try:
            reader = PdfReader(self.watermark_pdf_path)
            writer = PdfWriter()

            for page in reader.pages:
                width = float(page.mediabox.width)
                height = float(page.mediabox.height)
                watermark_page = self._build_watermark_page(width, height)
                page.merge_page(watermark_page)
                writer.add_page(page)

            save_path, _ = QFileDialog.getSaveFileName(self, "Simpan PDF Sebagai", "", "PDF Files (*.pdf)")
            if not save_path:
                return
            if not save_path.lower().endswith('.pdf'):
                save_path += '.pdf'
            with open(save_path, "wb") as f:
                writer.write(f)

            self.status_label_watermark.setText(f"✅ Disimpan ke {os.path.basename(save_path)}")
            QMessageBox.information(self, "Berhasil", "✅ Tanda air berhasil diterapkan")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"❌ Terjadi kesalahan: {str(e)}")

    # Shared file-list logic (Image tab & Merge PDF tab)
    def add_files_from_paths(self, paths_with_types):
        added = False
        for file_path, is_pdf in paths_with_types:
            if (file_path, is_pdf) not in self.file_paths:
                self.file_paths.append((file_path, is_pdf))
                added = True

        if not added:
            return False

        self.refresh_file_tables()
        self.refresh_image_cover_options()
        self.select_first_row(self.tool_stack.currentIndex() == 1)
        return True

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

            status_text = f"📄 {len(current_tab_files)} {'PDF' if is_pdf else 'gambar'} dipilih"
            if is_pdf:
                self.status_label_pdfs.setText(status_text)
            else:
                self.status_label_images.setText(status_text)

            self.refresh_file_tables()
            self.refresh_image_cover_options()
            self.select_first_row(is_pdf)

    def remove_file(self, index):
        if 0 <= index < len(self.file_paths):
            is_pdf = self.file_paths[index][1]
            self.file_paths.pop(index)
            self.selected_index = -1

            count = sum(1 for _, file_is_pdf in self.file_paths if file_is_pdf == is_pdf)
            status_text = f"📄 {count} {'PDF' if is_pdf else 'gambar'} tersisa"

            if is_pdf:
                self.status_label_pdfs.setText(status_text)
            else:
                self.status_label_images.setText(status_text)

            self.refresh_file_tables()
            self.update_side_preview(None, is_pdf)
            self.refresh_image_cover_options()

    def clear_all(self):
        self.file_paths = [fp for fp in self.file_paths if fp[1]]
        self.selected_index = -1
        self.status_label_images.setText("Pilih gambar untuk mulai")
        self.refresh_file_tables()
        self.update_side_preview(None, False)
        self.refresh_image_cover_options()

    def clear_all_pdfs(self):
        self.file_paths = [fp for fp in self.file_paths if not fp[1]]
        self.selected_index = -1
        self.status_label_pdfs.setText("Pilih PDF untuk mulai")
        self.refresh_file_tables()
        self.update_side_preview(None, True)

    def refresh_image_cover_options(self):
        if not hasattr(self, "cover_image_combo"):
            return

        current_path = self.cover_image_combo.currentData()
        image_files = [path for path, is_pdf in self.file_paths if not is_pdf]

        self.cover_image_combo.blockSignals(True)
        self.cover_image_combo.clear()
        self.cover_image_combo.addItem("Otomatis (gambar pertama)", None)

        for index, image_path in enumerate(image_files, start=1):
            self.cover_image_combo.addItem(f"{index}. {os.path.basename(image_path)}", image_path)

        if current_path and current_path in image_files:
            self.cover_image_combo.setCurrentIndex(image_files.index(current_path) + 1)
        else:
            self.cover_image_combo.setCurrentIndex(0)

        self.cover_image_combo.blockSignals(False)

    def _ordered_image_files_with_cover(self, image_files):
        if not image_files:
            return []

        selected_cover = self.cover_image_combo.currentData() if hasattr(self, "cover_image_combo") else None
        if not selected_cover or selected_cover not in image_files:
            return image_files

        ordered_files = [selected_cover]
        ordered_files.extend(path for path in image_files if path != selected_cover)
        return ordered_files

    def select_file(self, index):
        self.selected_index = index
        is_pdf = self.file_paths[index][1] if index < len(self.file_paths) else False
        self.select_row_by_index(is_pdf, index)

    def get_file_info(self, file_path, is_pdf):
        try:
            if is_pdf:
                if PYPDF2_AVAILABLE:
                    with open(file_path, 'rb') as f:
                        pdf_reader = PdfReader(f)
                        return f"{len(pdf_reader.pages)} halaman"
                return "PDF"
            if PIL_AVAILABLE:
                with Image.open(file_path) as img:
                    return f"{img.size[0]} x {img.size[1]} px"
                return "Image"
            return "Image"
        except Exception:
            return "Load error"

    def get_table_and_files(self, is_pdf):
        table = self.detail_table_pdfs if is_pdf else self.detail_table_images
        files = [(path, idx) for idx, (path, file_is_pdf) in enumerate(self.file_paths) if file_is_pdf == is_pdf]
        return table, files

    def refresh_file_tables(self):
        for is_pdf in (False, True):
            table, files = self.get_table_and_files(is_pdf)
            if table is None:
                continue
            table.blockSignals(True)
            table.setRowCount(len(files))
            for row, (file_path, original_index) in enumerate(files):
                number_item = QTableWidgetItem(str(row + 1))
                number_item.setTextAlignment(Qt.AlignCenter)
                table.setItem(row, 0, number_item)

                name_item = QTableWidgetItem(os.path.basename(file_path))
                name_item.setData(Qt.UserRole, original_index)
                table.setItem(row, 1, name_item)

                info_item = QTableWidgetItem(self.get_file_info(file_path, is_pdf))
                info_item.setTextAlignment(Qt.AlignCenter)
                table.setItem(row, 2, info_item)

                preview_item = QTableWidgetItem("Buka")
                preview_item.setTextAlignment(Qt.AlignCenter)
                table.setItem(row, 3, preview_item)
            table.blockSignals(False)
            if len(files) == 0:
                table.setRowCount(1)
                empty_item = QTableWidgetItem(f"Belum ada {'PDF' if is_pdf else 'gambar'} dipilih")
                empty_item.setTextAlignment(Qt.AlignCenter)
                table.setItem(0, 0, empty_item)
                table.setSpan(0, 0, 1, 4)
            else:
                table.clearSpans()

    def reorder_files(self, is_pdf, source_row, target_row):
        """
        Move a file from source_row to target_row within the visible rows
        of one tab (images or PDFs), then rebuild self.file_paths and the
        tables from that single source of truth.
        """
        table, files = self.get_table_and_files(is_pdf)
        if table is None or not files:
            return
        if not (0 <= source_row < len(files)) or not (0 <= target_row < len(files)):
            return
        if source_row == target_row:
            return

        reordered = files[:]
        moved_path, moved_original_index = reordered.pop(source_row)
        reordered.insert(target_row, (moved_path, moved_original_index))

        new_order = iter(path for path, _ in reordered)
        self.file_paths = [
            (next(new_order), file_is_pdf) if file_is_pdf == is_pdf else (path, file_is_pdf)
            for path, file_is_pdf in self.file_paths
        ]

        self.refresh_file_tables()
        self.select_file_by_path(moved_path, is_pdf)

    def select_first_row(self, is_pdf):
        table, files = self.get_table_and_files(is_pdf)
        if table is None or not files:
            self.update_side_preview(None, is_pdf)
            return
        table.selectRow(0)
        self.update_side_preview(files[0][0], is_pdf)

    def get_selected_table_index(self, is_pdf):
        table = self.detail_table_pdfs if is_pdf else self.detail_table_images
        if table is None:
            return -1
        rows = table.selectionModel().selectedRows() if table.selectionModel() else []
        return rows[0].row() if rows else -1

    def on_table_selection_changed(self, is_pdf):
        table, files = self.get_table_and_files(is_pdf)
        if table is None:
            return
        row = self.get_selected_table_index(is_pdf)
        if row < 0 or row >= len(files):
            self.update_side_preview(None, is_pdf)
            return
        file_path, original_index = files[row]
        self.selected_index = original_index
        self.update_side_preview(file_path, is_pdf)

    def on_table_double_clicked(self, is_pdf, row, column):
        table, files = self.get_table_and_files(is_pdf)
        if table is None or row < 0 or row >= len(files):
            return
        _, original_index = files[row]
        self.select_file(original_index)

    def select_row_by_index(self, is_pdf, original_index):
        table, files = self.get_table_and_files(is_pdf)
        if table is None:
            return
        for row, (_, idx) in enumerate(files):
            if idx == original_index:
                table.selectRow(row)
                self.update_side_preview(files[row][0], is_pdf)
                return

    def select_file_by_path(self, file_path, is_pdf):
        table, files = self.get_table_and_files(is_pdf)
        if table is None:
            return
        for row, (current_path, _) in enumerate(files):
            if current_path == file_path:
                table.selectRow(row)
                self.update_side_preview(current_path, is_pdf)
                return

    def update_side_preview(self, file_path, is_pdf):
        panel = self.preview_panels.get(is_pdf, {})
        image_label = panel.get('image')
        file_label = panel.get('file')
        info_label = panel.get('info')
        meta_label = panel.get('meta')

        if file_path is None:
            if image_label:
                image_label.setText("Pilih sebuah file")
                image_label.setPixmap(QPixmap())
            if file_label:
                file_label.setText("Belum ada file dipilih")
            if info_label:
                info_label.setText("")
            if meta_label:
                meta_label.setText("")
            self.preview_file_path = None
            return

        self.preview_file_path = file_path
        filename = os.path.basename(file_path)
        if file_label:
            file_label.setText(filename)

        try:
            if is_pdf:
                info_text = self.get_file_info(file_path, True)
                info_label.setText(info_text)
                meta_label.setText("Tipe: File PDF")
                image_label.setPixmap(QPixmap())
                image_label.setText("Preview PDF")
            else:
                info_text = self.get_file_info(file_path, False)
                info_label.setText(info_text)
                if PIL_AVAILABLE:
                    img = Image.open(file_path)
                    img = img.convert('RGBA') if img.mode != 'RGBA' else img
                    img.thumbnail((360, 240), Image.LANCZOS if hasattr(Image, 'LANCZOS') else Image.ANTIALIAS)
                    image_label.setText("")
                    image_label.setPixmap(pil_image_to_pixmap(img, (360, 240)))
                else:
                    image_label.setPixmap(QPixmap())
                    image_label.setText("Preview tidak tersedia")
                meta_label.setText("Klik dua kali baris untuk fokus")
        except Exception as e:
            image_label.setPixmap(QPixmap())
            image_label.setText("Preview error")
            info_label.setText(str(e))
            meta_label.setText("")

    def convert_to_pdf(self):
        if not PIL_AVAILABLE:
            QMessageBox.critical(self, "Error", "Pillow library is not available. Please install it first.")
            return

        image_files = [path for path, is_pdf in self.file_paths if not is_pdf]

        if not image_files:
            QMessageBox.warning(self, "Peringatan", "Pilih gambar terlebih dahulu")
            return

        image_files = self._ordered_image_files_with_cover(image_files)

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save PDF As",
            "",
            "PDF Files (*.pdf);;All Files (*)"
        )

        if file_path:
            try:
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

                    QMessageBox.information(self, "Berhasil", f"✅ PDF berhasil dibuat")
                    self.status_label_images.setText("Konversi selesai ✅")

            except Exception as e:
                QMessageBox.critical(self, "Error", f"❌ Terjadi kesalahan: {str(e)}")

    def merge_pdfs(self):
        if not PYPDF2_AVAILABLE:
            QMessageBox.critical(self, "Error", "PyPDF2 library is not available. Please install it first.")
            return

        pdf_files = [path for path, is_pdf in self.file_paths if is_pdf]

        if len(pdf_files) < 2:
            QMessageBox.warning(self, "Peringatan", "Pilih minimal 2 file PDF untuk digabungkan")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Merged PDF As",
            "",
            "PDF Files (*.pdf);;All Files (*)"
        )

        if file_path:
            try:
                if not file_path.lower().endswith('.pdf'):
                    file_path += '.pdf'

                merger = PdfMerger()

                for pdf_path in pdf_files:
                    merger.append(pdf_path)

                merger.write(file_path)
                merger.close()

                QMessageBox.information(self, "Berhasil", f"✅ PDF berhasil digabungkan")
                self.status_label_pdfs.setText("Penggabungan selesai ✅")

            except Exception as e:
                QMessageBox.critical(self, "Error", f"❌ Terjadi kesalahan: {str(e)}")

    def dragEnterEvent(self, event):
        if self._dropped_paths(event):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        paths = self._dropped_paths(event)
        if paths and self._handle_dropped_files(paths):
            event.acceptProposedAction()
            return
        event.ignore()


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    converter = EnhancedImageToPDFConverter()
    converter.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()