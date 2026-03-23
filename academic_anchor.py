import sys
import shutil
import os
import sqlite3

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QLineEdit, QTextEdit,
    QPushButton, QListWidget, QListWidgetItem, QVBoxLayout, QHBoxLayout,
    QGridLayout, QFileDialog, QComboBox, QDateTimeEdit, QGroupBox,
    QMessageBox, QSplitter, QSizePolicy
)

from PyQt6.QtCore import Qt, QDateTime
from PyQt6.QtGui import QColor, QIcon


DB_NAME = "academic_anchor.db"


# ---------------- DB INIT ---------------- #

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()

        cur.execute("""
        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            datetime TEXT,
            website TEXT,
            tag TEXT,
            content TEXT
        )
        """)

        conn.commit()


# ---------------- MAIN WINDOW ---------------- #

class MainWindow(QMainWindow):

    TAG_COLORS = {
        "Other": "#B0BEC5",
        "OSINT": "#FFB74D",
        "Cyber Security": "#E57373",
        "Programming": "#64B5F6",
        "News": "#AED581",
        "Academic Work": "#BA68C8",
        "Internet": "#4DB6AC",
        "Book": "#FFD54F",
        "Research Paper": "#7986CB",
        "Thesis / Dissertation": "#A1887F",
        "Lecture Notes": "#4FC3F7",
        "Lab Work": "#81C784",
        "Experiment": "#F06292",
        "AI / Machine Learning": "#FF8A65",
        "Data Science": "#4DD0E1",
        "Networking": "#90A4AE",
        "Software Tools": "#DCE775",
        "Hardware": "#FFCC80",
        "Threat Intelligence": "#F44336",
        "Malware Analysis": "#FF7043",
        "Pentesting": "#9575CD",
        "Phishing / Scam": "#7986CB",
        "Digital Forensics": "#64DD17",
        "To-Do": "#B39DDB",
        "Idea": "#F48FB1",
        "Project": "#FFAB91",
        "Reminder": "#AED581",
        "Checklist": "#81D4FA",
        "Article": "#FFD54F",
        "Video": "#4DB6AC",
        "Podcast": "#E57373",
        "Tutorial": "#BA68C8",
        "Book Summary": "#FFB74D",
        "Reference": "#A1887F",
        "Inspiration": "#4FC3F7",
        "Quote": "#64B5F6",
        "Event": "#FF8A65",
        "Web Resource": "#DCE775"
    }

    # ---------------- INIT ---------------- #

    def __init__(self):
        super().__init__()

        self.setWindowIcon(QIcon("ico.ico"))

        self.setWindowTitle("Academic Anchor")
        self.resize(1100, 750)

        init_db()

        self.selected_id = None
        self.rows = []

        self.init_ui()
        self.load_list()

        self.setStyleSheet("""
        QListWidget::item:hover { background: #e0e0e0; }
        QListWidget::item:selected { background: #90CAF9; }
        """)

    # ---------------- SAFE DB ---------------- #

    def connect_db(self):

        if not os.path.exists(DB_NAME):
            init_db()

        return sqlite3.connect(DB_NAME)

    # ---------------- UI ---------------- #

    def init_ui(self):

        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        # ---------- LEFT ----------

        left_panel = QWidget()
        left_layout = QVBoxLayout()

        self.list_widget = QListWidget()
        self.list_widget.setAlternatingRowColors(True)

        self.list_widget.itemClicked.connect(self.load_selected)
        self.list_widget.itemDoubleClicked.connect(self.load_selected)

        left_layout.addWidget(QLabel("Entries"))
        left_layout.addWidget(self.list_widget)

        left_panel.setLayout(left_layout)

        # ---------- RIGHT ----------

        right_panel = QWidget()
        form_layout = QVBoxLayout()

        form_group = QGroupBox("Entry Form")
        grid = QGridLayout()

        self.title_input = QLineEdit()

        self.datetime_input = QDateTimeEdit()
        self.datetime_input.setCalendarPopup(True)
        self.datetime_input.setDateTime(QDateTime.currentDateTime())

        self.website_input = QLineEdit()

        self.tag_input = QComboBox()
        self.tag_input.setEditable(True)

        tags = list(self.TAG_COLORS.keys())
        self.tag_input.addItems(tags)

        self.content_input = QTextEdit()
        self.content_input.setMinimumHeight(300)
        self.content_input.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )

        grid.addWidget(QLabel("Title:"), 0, 0)
        grid.addWidget(self.title_input, 0, 1)

        grid.addWidget(QLabel("Date:"), 1, 0)
        grid.addWidget(self.datetime_input, 1, 1)

        grid.addWidget(QLabel("Website:"), 2, 0)
        grid.addWidget(self.website_input, 2, 1)

        grid.addWidget(QLabel("Tag:"), 3, 0)
        grid.addWidget(self.tag_input, 3, 1)

        grid.addWidget(QLabel("Content:"), 4, 0)
        grid.addWidget(self.content_input, 4, 1)

        form_group.setLayout(grid)
        form_layout.addWidget(form_group)

        # ---------- BUTTONS ----------

        btn_layout = QHBoxLayout()

        add_btn = QPushButton("Add / Update")
        add_btn.setStyleSheet("background:#4CAF50;color:white;")

        del_btn = QPushButton("Delete")
        del_btn.setStyleSheet("background:#c62828;color:white;")

        clear_btn = QPushButton("Clear")
        clear_btn.setStyleSheet("background:#757575;color:white;")

        add_btn.clicked.connect(self.add_entry)
        del_btn.clicked.connect(self.delete_entry)
        clear_btn.clicked.connect(self.clear_form)

        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(del_btn)
        btn_layout.addWidget(clear_btn)

        form_layout.addLayout(btn_layout)

        # ---------- SEARCH ----------

        search_layout = QHBoxLayout()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search...")
        self.search_input.textChanged.connect(self.load_list)

        self.filter_tag = QComboBox()
        self.filter_tag.addItem("All")
        self.filter_tag.addItems(tags)
        self.filter_tag.currentTextChanged.connect(self.load_list)

        search_layout.addWidget(QLabel("Search"))
        search_layout.addWidget(self.search_input)

        search_layout.addWidget(QLabel("Tag"))
        search_layout.addWidget(self.filter_tag)

        form_layout.addLayout(search_layout)

        # ---------- DB ----------

        db_layout = QHBoxLayout()

        export_btn = QPushButton("Export DB")
        import_btn = QPushButton("Import DB")
        quit_btn = QPushButton("Quit")

        export_btn.clicked.connect(self.export_db)
        import_btn.clicked.connect(self.import_db)
        quit_btn.clicked.connect(self.close)

        db_layout.addWidget(export_btn)
        db_layout.addWidget(import_btn)
        db_layout.addStretch()
        db_layout.addWidget(quit_btn)

        form_layout.addLayout(db_layout)

        right_panel.setLayout(form_layout)

        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)

        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)

        main_layout.addWidget(splitter)

        # ---------- FOOTER ----------

        footer = QLabel("AcademicAnchor • 2026")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer.setMaximumHeight(14)

        footer.setStyleSheet("""
        color: gray;
        font-size: 9px;
        margin:0;
        padding:0;
        """)

        main_layout.addWidget(footer, stretch=0)

        central.setLayout(main_layout)

    # ---------------- CRUD ---------------- #

    def add_entry(self):

        title = self.title_input.text().strip()

        if not title:
            QMessageBox.warning(self, "Error", "Title required")
            return

        dt = self.datetime_input.dateTime().toString(
            "yyyy-MM-dd hh:mm:ss"
        )

        website = self.website_input.text().strip()
        tag = self.tag_input.currentText().strip()
        content = self.content_input.toPlainText().strip()

        with self.connect_db() as conn:

            cur = conn.cursor()

            if self.selected_id:

                cur.execute("""
                UPDATE entries
                SET title=?, datetime=?, website=?, tag=?, content=?
                WHERE id=?
                """, (title, dt, website, tag, content,
                      self.selected_id))

            else:

                cur.execute("""
                INSERT INTO entries
                (title, datetime, website, tag, content)
                VALUES (?, ?, ?, ?, ?)
                """, (title, dt, website, tag, content))

            conn.commit()

        self.load_list()

        if self.selected_id:
            for i in range(self.list_widget.count()):
                item = self.list_widget.item(i)
                if item.data(Qt.ItemDataRole.UserRole) == self.selected_id:
                    self.list_widget.setCurrentItem(item)
                    break

        self.clear_form()

    # ---------------- LIST ---------------- #

    def load_list(self):

        self.list_widget.clear()

        search = self.search_input.text()
        tag = self.filter_tag.currentText()

        query = """
        SELECT id,title,datetime,tag,content
        FROM entries
        WHERE 1=1
        """

        params = []

        if search:
            query += """
            AND (
                LOWER(title) LIKE LOWER(?)
                OR LOWER(content) LIKE LOWER(?)
            )
            """
            params += [f"%{search}%", f"%{search}%"]

        if tag != "All":
            query += " AND tag=?"
            params.append(tag)

        query += " ORDER BY datetime DESC"

        with self.connect_db() as conn:

            cur = conn.cursor()
            cur.execute(query, params)

            self.rows = cur.fetchall()

        for r in self.rows:

            text = r[1][:50] + "..." if len(r[1]) > 50 else r[1]

            item = QListWidgetItem(
                f"{text} | {r[2]} | {r[3]}"
            )

            color = self.TAG_COLORS.get(
                r[3], "#E0E0E0"
            )

            item.setBackground(QColor(color))

            item.setData(
                Qt.ItemDataRole.UserRole,
                r[0]
            )

            self.list_widget.addItem(item)

    # ---------------- SELECT ---------------- #

    def load_selected(self, item):

        self.selected_id = item.data(
            Qt.ItemDataRole.UserRole
        )

        with self.connect_db() as conn:

            cur = conn.cursor()

            cur.execute(
                "SELECT * FROM entries WHERE id=?",
                (self.selected_id,)
            )

            r = cur.fetchone()

        if not r:
            return

        self.title_input.setText(r[1])

        dt = QDateTime.fromString(
            r[2],
            "yyyy-MM-dd hh:mm:ss"
        )

        if not dt.isValid():
            dt = QDateTime.currentDateTime()

        self.datetime_input.setDateTime(dt)

        self.website_input.setText(r[3])
        self.tag_input.setCurrentText(r[4])
        self.content_input.setPlainText(r[5])

    # ---------------- DELETE ---------------- #

    def delete_entry(self):

        if not self.selected_id:
            return

        reply = QMessageBox.question(
            self,
            "Delete",
            "Delete selected entry?",
            QMessageBox.StandardButton.Yes |
            QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        with self.connect_db() as conn:

            cur = conn.cursor()

            cur.execute(
                "DELETE FROM entries WHERE id=?",
                (self.selected_id,)
            )

            conn.commit()

        self.load_list()
        self.clear_form()

    # ---------------- CLEAR ---------------- #

    def clear_form(self):

        self.selected_id = None

        self.title_input.clear()
        self.website_input.clear()
        self.content_input.clear()

        self.tag_input.setCurrentIndex(0)

        self.datetime_input.setDateTime(
            QDateTime.currentDateTime()
        )

    # ---------------- EXPORT ---------------- #

    def export_db(self):

        file, _ = QFileDialog.getSaveFileName(
            self,
            "Export DB",
            DB_NAME,
            "SQLite (*.db)"
        )

        if file:
            shutil.copy(DB_NAME, file)

    # ---------------- IMPORT ---------------- #

    def import_db(self):

        file, _ = QFileDialog.getOpenFileName(
            self,
            "Import DB",
            "",
            "SQLite (*.db)"
        )

        if not file:
            return

        reply = QMessageBox.question(
            self,
            "Import",
            "Replace DB?",
            QMessageBox.StandardButton.Yes |
            QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        with sqlite3.connect(file) as src:
            with sqlite3.connect(DB_NAME) as dest:
                src.backup(dest)

        self.load_list()


# ---------------- MAIN ---------------- #

if __name__ == "__main__":

    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
