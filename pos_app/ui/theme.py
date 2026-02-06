"""UI theme settings."""
DARK_STYLESHEET = """
QWidget {
    background-color: #111827;
    color: #F9FAFB;
    font-family: 'Segoe UI', sans-serif;
    font-size: 12pt;
}
QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {
    background-color: #1F2937;
    border: 1px solid #374151;
    border-radius: 6px;
    padding: 6px;
}
QPushButton {
    background-color: #2563EB;
    border: none;
    border-radius: 8px;
    padding: 8px 12px;
}
QPushButton:hover {
    background-color: #3B82F6;
}
QPushButton:disabled {
    background-color: #6B7280;
}
QTableWidget {
    background-color: #1F2937;
    gridline-color: #374151;
    border: 1px solid #374151;
}
QHeaderView::section {
    background-color: #111827;
    border: 1px solid #374151;
    padding: 6px;
}
QListWidget {
    background-color: #1F2937;
    border: 1px solid #374151;
}
"""
