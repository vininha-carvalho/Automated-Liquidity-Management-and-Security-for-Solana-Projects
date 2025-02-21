import sys
import asyncio
import time
from PyQt5 import QtWidgets, QtCore
import qasync

class TradingTerminal(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.running = False
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Crypto Trading Terminal MVP")
        self.resize(1000, 700)
        
        # Основной макет
        main_layout = QtWidgets.QVBoxLayout(self)
        
        # Панель настроек стратегии
        settings_group = QtWidgets.QGroupBox("Trade settings")
        settings_layout = QtWidgets.QFormLayout(settings_group)
        
        # Поля ввода токенов (до 10, здесь пример для одного)
        self.token_input = QtWidgets.QLineEdit()
        self.token_input.setPlaceholderText("Введите адрес контракта токена")
        settings_layout.addRow("Токен:", self.token_input)
        
        # Выбор интервала данных
        self.interval_input = QtWidgets.QComboBox()
        self.interval_input.addItems(["1s", "5s", "15s", "30s", "1m", "2m", "3m", "5m"])
        settings_layout.addRow("Data interval:", self.interval_input)
        
        # Процент аллокации для ордеров
        self.allocation_input = QtWidgets.QLineEdit("10")
        settings_layout.addRow("Аллокация (%)", self.allocation_input)
        
        # Кнопки управления
        btn_layout = QtWidgets.QHBoxLayout()
        self.start_button = QtWidgets.QPushButton("Запустить торговлю")
        self.stop_button = QtWidgets.QPushButton("Остановить торговлю")
        btn_layout.addWidget(self.start_button)
        btn_layout.addWidget(self.stop_button)
        settings_layout.addRow(btn_layout)
        
        main_layout.addWidget(settings_group)
        
        # Панель отображения метрик в реальном времени
        metrics_group = QtWidgets.QGroupBox("Метрики в реальном времени")
        metrics_layout = QtWidgets.QVBoxLayout(metrics_group)
        self.metrics_text = QtWidgets.QTextEdit()
        self.metrics_text.setReadOnly(True)
        metrics_layout.addWidget(self.metrics_text)
        main_layout.addWidget(metrics_group)
        
        orders_group = QtWidgets.QGroupBox("History of warrants")
        orders_layout = QtWidgets.QVBoxLayout(orders_group)
        self.orders_table = QtWidgets.QTableWidget()
        self.orders_table.setColumnCount(5)
        self.orders_table.setHorizontalHeaderLabels(["Time", "Действие", "Action", "Quantity", "Status"])
        orders_layout.addWidget(self.orders_table)
        main_layout.addWidget(orders_group)
        
        self.start_button.clicked.connect(self.start_trading)
        self.stop_button.clicked.connect(self.stop_trading)
    
    def log_metric(self, message: str):
        current_time = time.strftime("%H:%M:%S")
        self.metrics_text.append(f"[{current_time}] {message}")
    
    async def trading_loop(self):
        self.running = True
        counter = 0
        while self.running:
            self.log_metric(f"Metrics update: order executed#{counter}")
            
            row = self.orders_table.rowCount()
            self.orders_table.insertRow(row)
            self.orders_table.setItem(row, 0, QtWidgets.QTableWidgetItem(time.strftime("%H:%M:%S")))
            self.orders_table.setItem(row, 1, QtWidgets.QTableWidgetItem("Buy"))
            self.orders_table.setItem(row, 2, QtWidgets.QTableWidgetItem(self.token_input.text()))
            self.orders_table.setItem(row, 3, QtWidgets.QTableWidgetItem("0.001"))
            self.orders_table.setItem(row, 4, QtWidgets.QTableWidgetItem("Executed"))
            
            counter += 1
            await asyncio.sleep(1)  
    
    def start_trading(self):
        self.log_metric("Trading is up and running.")
        asyncio.ensure_future(self.trading_loop())
    
    def stop_trading(self):
        self.running = False
        self.log_metric("Trade is halted.")

def main():
    app = QtWidgets.QApplication(sys.argv)
    loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(loop)
    
    window = TradingTerminal()
    window.show()
    
    with loop:
        loop.run_forever()

if __name__ == "__main__":
    main()
