import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QPushButton, QGridLayout, 
                             QTabWidget, QVBoxLayout)
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QFont

class BossTracker(QWidget):
    def __init__(self):
        super().__init__()
        self.boss_names = ["Subora", "Ultumuno", "Nazrudin"]
        self.timers_per_boss = {}  # Dicionário para guardar timers por boss
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Word Boss Tracker')
        self.setGeometry(100, 100, 900, 600)

        layout = QVBoxLayout()
        self.tab_widget = QTabWidget()
        
        # Adiciona uma aba para cada boss
        for boss in self.boss_names:
            tab = QWidget()
            tab_layout = QGridLayout()
            self.initTab(tab_layout, boss)
            tab.setLayout(tab_layout)
            self.tab_widget.addTab(tab, boss)

        layout.addWidget(self.tab_widget)
        self.setLayout(layout)

        # Estilos básicos
        self.setStyleSheet("""
            QLabel {
                font-size: 18px;
                padding: 5px;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 16px;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)

    def initTab(self, layout, boss):
        # Inicializa os timers e labels para cada boss
        self.timers_per_boss[boss] = {
            'timer_objects': [None] * 8,
            'timers': [3600 for _ in range(8)],  # 1 hora (3600 segundos) para cada canal
            'labels': []
        }

        # Criar 8 canais para cada aba
        for i in range(8):
            label = QLabel(f'Canal {i+1}')
            label.setFont(QFont('Arial', 20))
            timer_label = QLabel('00:00:00')
            timer_label.setFont(QFont('Arial', 25))
            button = QPushButton('Boss Derrotado')
            
            # Aqui passamos o valor de `i` corretamente para o botão
            button.clicked.connect(lambda _, ch=i, b=boss: self.boss_killed(ch, b))
            
            layout.addWidget(label, i, 0)
            layout.addWidget(timer_label, i, 1)
            layout.addWidget(button, i, 2)
            
            # Armazenar os labels e inicializar os timers
            self.timers_per_boss[boss]['labels'].append(timer_label)
            self.timers_per_boss[boss]['timer_objects'][i] = QTimer(self)

    def boss_killed(self, channel, boss):
        label = self.timers_per_boss[boss]['labels'][channel]
        self.start_timer(channel, boss, 3600)  # Reiniciar contagem de 1 hora (3600 segundos)

    def start_timer(self, channel, boss, seconds):
        label = self.timers_per_boss[boss]['labels'][channel]
        timer = self.timers_per_boss[boss]['timer_objects'][channel]

        # Resetar o timer atual
        timer.stop()
        self.timers_per_boss[boss]['timers'][channel] = seconds

        # Conectar o timer e reiniciar
        timer.timeout.connect(lambda: self.update_timer(channel, boss, label, timer))
        timer.start(1000)  # Atualiza a cada segundo

    def update_timer(self, channel, boss, label, timer):
        self.timers_per_boss[boss]['timers'][channel] -= 1
        minutes, seconds = divmod(self.timers_per_boss[boss]['timers'][channel], 60)
        label.setText(f'{minutes:02d}:{seconds:02d}')
        
        # Alerta quando faltam 5 minutos (300 segundos)
        if self.timers_per_boss[boss]['timers'][channel] == 300:
            label.setStyleSheet("color: red;")
        
        if self.timers_per_boss[boss]['timers'][channel] <= 0:
            timer.stop()
            label.setText('Boss Vivo!')
            label.setStyleSheet("color: black;")  # Reset the color

# Inicializar o aplicativo
app = QApplication(sys.argv)
tracker = BossTracker()
tracker.show()
sys.exit(app.exec_())  # Mantém o loop de eventos do PyQt5 rodando
