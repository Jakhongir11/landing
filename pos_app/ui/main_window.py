"""Main window and screens for the POS system."""
from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from pos_app.controllers.product_controller import ProductController
from pos_app.controllers.sale_controller import SaleController
from pos_app.models import SaleItem


@dataclass
class CartRow:
    product_id: int
    name: str
    quantity: int
    price: float

    @property
    def total(self) -> float:
        return self.quantity * self.price


class SalesScreen(QWidget):
    def __init__(self, product_controller: ProductController, sale_controller: SaleController) -> None:
        super().__init__()
        self.product_controller = product_controller
        self.sale_controller = sale_controller
        self.cart: list[CartRow] = []
        self._build_ui()
        self._configure_shortcuts()
        self.refresh_products()

    def _build_ui(self) -> None:
        layout = QHBoxLayout(self)

        left_panel = QVBoxLayout()
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск товара...")
        self.search_button = QPushButton("Найти")
        self.search_button.clicked.connect(self.handle_search)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_button)

        self.products_table = QTableWidget(0, 3)
        self.products_table.setHorizontalHeaderLabels(["Товар", "Цена", "Категория"])
        self.products_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.products_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.products_table.horizontalHeader().setStretchLastSection(True)
        self.products_table.verticalHeader().setVisible(False)

        add_layout = QHBoxLayout()
        self.quantity_spin = QSpinBox()
        self.quantity_spin.setRange(1, 99)
        self.add_button = QPushButton("Добавить в чек")
        self.add_button.clicked.connect(self.add_to_cart)
        add_layout.addWidget(QLabel("Количество:"))
        add_layout.addWidget(self.quantity_spin)
        add_layout.addWidget(self.add_button)

        left_panel.addLayout(search_layout)
        left_panel.addWidget(self.products_table)
        left_panel.addLayout(add_layout)

        right_panel = QVBoxLayout()
        right_panel.addWidget(QLabel("Текущий чек"))

        self.cart_table = QTableWidget(0, 4)
        self.cart_table.setHorizontalHeaderLabels(["Товар", "Кол-во", "Цена", "Итого"])
        self.cart_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.cart_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.cart_table.horizontalHeader().setStretchLastSection(True)
        self.cart_table.verticalHeader().setVisible(False)

        totals_layout = QHBoxLayout()
        self.total_label = QLabel("Итого: 0 ₽")
        totals_layout.addWidget(self.total_label)
        totals_layout.addStretch()

        actions_layout = QHBoxLayout()
        self.pay_button = QPushButton("Оплатить")
        self.pay_button.clicked.connect(self.complete_sale)
        self.clear_button = QPushButton("Очистить")
        self.clear_button.clicked.connect(self.clear_cart)
        actions_layout.addWidget(self.pay_button)
        actions_layout.addWidget(self.clear_button)

        right_panel.addWidget(self.cart_table)
        right_panel.addLayout(totals_layout)
        right_panel.addLayout(actions_layout)

        layout.addLayout(left_panel, 2)
        layout.addLayout(right_panel, 1)

    def _configure_shortcuts(self) -> None:
        QShortcut(QKeySequence("Ctrl+F"), self, activated=self.search_input.setFocus)
        QShortcut(QKeySequence("Ctrl+N"), self, activated=self.clear_cart)
        QShortcut(QKeySequence("Ctrl+P"), self, activated=self.complete_sale)

    def refresh_products(self, query: str | None = None) -> None:
        products = (
            self.product_controller.search_products(query)
            if query
            else self.product_controller.list_products()
        )
        self.products_table.setRowCount(0)
        for row_index, product in enumerate(products):
            self.products_table.insertRow(row_index)
            name_item = QTableWidgetItem(product["name"])
            name_item.setData(Qt.ItemDataRole.UserRole, product)
            self.products_table.setItem(row_index, 0, name_item)
            self.products_table.setItem(
                row_index, 1, QTableWidgetItem(f"{product['price']:.2f} ₽")
            )
            self.products_table.setItem(row_index, 2, QTableWidgetItem(product["category"]))
            self.products_table.setRowHeight(row_index, 28)

    def handle_search(self) -> None:
        query = self.search_input.text().strip()
        self.refresh_products(query if query else None)

    def add_to_cart(self) -> None:
        selected = self.products_table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Выбор товара", "Выберите товар из списка.")
            return
        product_item = self.products_table.item(selected, 0)
        if not product_item:
            return
        product = product_item.data(Qt.ItemDataRole.UserRole)
        quantity = self.quantity_spin.value()
        for row in self.cart:
            if row.product_id == product["id"]:
                row.quantity += quantity
                self.refresh_cart()
                return
        self.cart.append(
            CartRow(
                product_id=product["id"],
                name=product["name"],
                quantity=quantity,
                price=product["price"],
            )
        )
        self.refresh_cart()

    def refresh_cart(self) -> None:
        self.cart_table.setRowCount(0)
        total = 0.0
        for row_index, item in enumerate(self.cart):
            self.cart_table.insertRow(row_index)
            self.cart_table.setItem(row_index, 0, QTableWidgetItem(item.name))
            self.cart_table.setItem(row_index, 1, QTableWidgetItem(str(item.quantity)))
            self.cart_table.setItem(row_index, 2, QTableWidgetItem(f"{item.price:.2f} ₽"))
            self.cart_table.setItem(row_index, 3, QTableWidgetItem(f"{item.total:.2f} ₽"))
            self.cart_table.setRowHeight(row_index, 28)
            total += item.total
        self.total_label.setText(f"Итого: {total:.2f} ₽")

    def clear_cart(self) -> None:
        self.cart.clear()
        self.refresh_cart()

    def complete_sale(self) -> None:
        if not self.cart:
            QMessageBox.information(self, "Оплата", "Чек пуст.")
            return
        items = [
            SaleItem(
                product_id=row.product_id,
                name=row.name,
                quantity=row.quantity,
                price=row.price,
            )
            for row in self.cart
        ]
        sale_id = self.sale_controller.create_sale(items)
        receipt_lines = [f"Чек №{sale_id}"]
        for item in items:
            receipt_lines.append(f"{item.name} x{item.quantity} = {item.total:.2f} ₽")
        receipt_lines.append(self.total_label.text())
        QMessageBox.information(self, "Печать чека", "\n".join(receipt_lines))
        self.clear_cart()


class ProductsScreen(QWidget):
    def __init__(self, product_controller: ProductController) -> None:
        super().__init__()
        self.product_controller = product_controller
        self._build_ui()
        self.refresh_products()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)

        form_group = QGroupBox("Новый товар")
        form_layout = QFormLayout(form_group)
        self.name_input = QLineEdit()
        self.price_input = QDoubleSpinBox()
        self.price_input.setRange(0.0, 99999.0)
        self.price_input.setDecimals(2)
        self.category_input = QLineEdit()
        self.add_button = QPushButton("Добавить")
        self.add_button.clicked.connect(self.add_product)

        form_layout.addRow("Название", self.name_input)
        form_layout.addRow("Цена", self.price_input)
        form_layout.addRow("Категория", self.category_input)
        form_layout.addRow(self.add_button)

        self.products_table = QTableWidget(0, 4)
        self.products_table.setHorizontalHeaderLabels(["ID", "Товар", "Цена", "Категория"])
        self.products_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.products_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.products_table.horizontalHeader().setStretchLastSection(True)
        self.products_table.verticalHeader().setVisible(False)

        self.delete_button = QPushButton("Удалить выбранный")
        self.delete_button.clicked.connect(self.delete_product)

        layout.addWidget(form_group)
        layout.addWidget(self.products_table)
        layout.addWidget(self.delete_button)

    def refresh_products(self) -> None:
        products = self.product_controller.list_products()
        self.products_table.setRowCount(0)
        for row_index, product in enumerate(products):
            self.products_table.insertRow(row_index)
            self.products_table.setItem(row_index, 0, QTableWidgetItem(str(product["id"])))
            self.products_table.setItem(row_index, 1, QTableWidgetItem(product["name"]))
            self.products_table.setItem(
                row_index, 2, QTableWidgetItem(f"{product['price']:.2f} ₽")
            )
            self.products_table.setItem(row_index, 3, QTableWidgetItem(product["category"]))
            self.products_table.setRowHeight(row_index, 28)

    def add_product(self) -> None:
        name = self.name_input.text().strip()
        category = self.category_input.text().strip()
        price = self.price_input.value()
        if not name or not category or price <= 0:
            QMessageBox.warning(self, "Ошибка", "Заполните все поля корректно.")
            return
        self.product_controller.add_product(name, price, category)
        self.name_input.clear()
        self.category_input.clear()
        self.price_input.setValue(0.0)
        self.refresh_products()

    def delete_product(self) -> None:
        selected = self.products_table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Удаление", "Выберите товар для удаления.")
            return
        product_id = int(self.products_table.item(selected, 0).text())
        self.product_controller.delete_product(product_id)
        self.refresh_products()


class HistoryScreen(QWidget):
    def __init__(self, sale_controller: SaleController) -> None:
        super().__init__()
        self.sale_controller = sale_controller
        self._build_ui()
        self.refresh_sales()

    def _build_ui(self) -> None:
        layout = QHBoxLayout(self)

        left_panel = QVBoxLayout()
        left_panel.addWidget(QLabel("История чеков"))
        self.sales_table = QTableWidget(0, 3)
        self.sales_table.setHorizontalHeaderLabels(["ID", "Сумма", "Дата"])
        self.sales_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.sales_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.sales_table.horizontalHeader().setStretchLastSection(True)
        self.sales_table.verticalHeader().setVisible(False)
        self.sales_table.itemSelectionChanged.connect(self.load_details)

        left_panel.addWidget(self.sales_table)

        right_panel = QVBoxLayout()
        right_panel.addWidget(QLabel("Детали чека"))
        self.items_table = QTableWidget(0, 3)
        self.items_table.setHorizontalHeaderLabels(["Товар", "Кол-во", "Цена"])
        self.items_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.items_table.horizontalHeader().setStretchLastSection(True)
        self.items_table.verticalHeader().setVisible(False)
        right_panel.addWidget(self.items_table)

        layout.addLayout(left_panel, 2)
        layout.addLayout(right_panel, 1)

    def refresh_sales(self) -> None:
        sales = self.sale_controller.list_sales()
        self.sales_table.setRowCount(0)
        for row_index, sale in enumerate(sales):
            self.sales_table.insertRow(row_index)
            self.sales_table.setItem(row_index, 0, QTableWidgetItem(str(sale["id"])))
            self.sales_table.setItem(
                row_index, 1, QTableWidgetItem(f"{sale['total']:.2f} ₽")
            )
            self.sales_table.setItem(row_index, 2, QTableWidgetItem(sale["created_at"]))
            self.sales_table.setRowHeight(row_index, 28)

    def load_details(self) -> None:
        selected = self.sales_table.currentRow()
        if selected < 0:
            return
        sale_id = int(self.sales_table.item(selected, 0).text())
        items = self.sale_controller.list_sale_items(sale_id)
        self.items_table.setRowCount(0)
        for row_index, item in enumerate(items):
            self.items_table.insertRow(row_index)
            self.items_table.setItem(row_index, 0, QTableWidgetItem(item["name"]))
            self.items_table.setItem(row_index, 1, QTableWidgetItem(str(item["quantity"])))
            self.items_table.setItem(
                row_index, 2, QTableWidgetItem(f"{item['price']:.2f} ₽")
            )
            self.items_table.setRowHeight(row_index, 28)


class MainWindow(QMainWindow):
    def __init__(self, product_controller: ProductController, sale_controller: SaleController) -> None:
        super().__init__()
        self.product_controller = product_controller
        self.sale_controller = sale_controller
        self.setWindowTitle("POS Light")
        self.resize(1200, 720)
        self._build_ui()

    def _build_ui(self) -> None:
        wrapper = QWidget()
        main_layout = QHBoxLayout(wrapper)

        nav = QVBoxLayout()
        nav.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.sales_button = QPushButton("Продажи")
        self.products_button = QPushButton("Товары")
        self.history_button = QPushButton("История")
        nav.addWidget(self.sales_button)
        nav.addWidget(self.products_button)
        nav.addWidget(self.history_button)
        nav.addStretch()

        self.stack = QStackedWidget()
        self.sales_screen = SalesScreen(self.product_controller, self.sale_controller)
        self.products_screen = ProductsScreen(self.product_controller)
        self.history_screen = HistoryScreen(self.sale_controller)
        self.stack.addWidget(self.sales_screen)
        self.stack.addWidget(self.products_screen)
        self.stack.addWidget(self.history_screen)

        self.sales_button.clicked.connect(lambda: self.switch_screen(0))
        self.products_button.clicked.connect(lambda: self.switch_screen(1))
        self.history_button.clicked.connect(lambda: self.switch_screen(2))

        main_layout.addLayout(nav, 1)
        main_layout.addWidget(self.stack, 5)
        self.setCentralWidget(wrapper)

    def switch_screen(self, index: int) -> None:
        self.stack.setCurrentIndex(index)
        if index == 1:
            self.products_screen.refresh_products()
        if index == 2:
            self.history_screen.refresh_sales()
