"""Entry point for the POS system."""
from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from pos_app.controllers.product_controller import ProductController
from pos_app.controllers.sale_controller import SaleController
from pos_app.database import DatabaseManager
from pos_app.ui.main_window import MainWindow
from pos_app.ui.theme import DARK_STYLESHEET


def main() -> int:
    app = QApplication(sys.argv)
    app.setStyleSheet(DARK_STYLESHEET)

    db = DatabaseManager()
    product_controller = ProductController(db)
    sale_controller = SaleController(db)

    window = MainWindow(product_controller, sale_controller)
    window.show()

    exit_code = app.exec()
    db.close()
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
