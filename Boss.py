import sys
import json
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QPushButton, QGridLayout, 
                             QTabWidget, QVBoxLayout, QMessageBox, QScrollArea, QLineEdit, QHBoxLayout)
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QFont

class BossTracker(QWidget):
    def __init__(self):
        super().__init__()
        self.boss_names = ["Subora", "Ultumuno", "Nazrudin"]
        self.timers_per_boss = {}  # Dicionário para guardar timers por boss
        self.initUI()
        self.load_state()  # Carregar o estado dos timers ao iniciar

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
        
        # Scrollable History
        self.history_area = QScrollArea()
        self.history_content = QLabel("Histórico de eventos:")
        self.history_content.setWordWrap(True)
        self.history_area.setWidget(self.history_content)
        self.history_area.setWidgetResizable(True)
        self.history_area.setFixedHeight(150)
        layout.addWidget(self.history_area)

        # Botão para limpar o histórico
        clear_history_button = QPushButton("Limpar Histórico")
        clear_history_button.clicked.connect(self.clear_history)
        layout.addWidget(clear_history_button)

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
            
            # Entrada para definir manualmente o tempo
            time_input = QLineEdit()
            time_input.setPlaceholderText("Tempo (segundos)")
            
            button = QPushButton('Boss Derrotado')
            button.clicked.connect(lambda _, ch=i, b=boss, t_input=time_input: self.boss_killed(ch, b, t_input))

            layout.addWidget(label, i, 0)
            layout.addWidget(timer_label, i, 1)
            layout.addWidget(time_input, i, 2)
            layout.addWidget(button, i, 3)
            
            # Armazenar os labels e inicializar os timers
            self.timers_per_boss[boss]['labels'].append(timer_label)
            self.timers_per_boss[boss]['timer_objects'][i] = QTimer(self)

    def boss_killed(self, channel, boss, time_input):
        # Definir o tempo manualmente para teste se fornecido
        try:
            seconds = int(time_input.text()) if time_input.text() else 3600
        except ValueError:
            seconds = 3600  # Valor padrão se a entrada for inválida

        label = self.timers_per_boss[boss]['labels'][channel]
        self.start_timer(channel, boss, seconds)  # Reiniciar contagem

        # Atualizar o histórico
        self.update_history(f"Boss {boss} no Canal {channel + 1} foi morto!")

    def start_timer(self, channel, boss, seconds):
        label = self.timers_per_boss[boss]['labels'][channel]
        timer = self.timers_per_boss[boss]['timer_objects'][channel]

        # Resetar o timer atual
        timer.stop()
        self.timers_per_boss[boss]['timers'][channel] = seconds

        # Conectar o timer e reiniciar
        timer.timeout.connect(lambda: self.update_timer(channel, boss, label, timer))
        timer.start(1000)  # Atualiza a cada segundo

        # Salvar o estado dos timers
        self.save_state()

    def update_timer(self, channel, boss, label, timer):
        self.timers_per_boss[boss]['timers'][channel] -= 1
        minutes, seconds = divmod(self.timers_per_boss[boss]['timers'][channel], 60)
        label.setText(f'{minutes:02d}:{seconds:02d}')
        
        # Notificação visual quando faltam 5 minutos
        if self.timers_per_boss[boss]['timers'][channel] == 300:
            self.show_alert(f"Faltam 5 minutos para o boss {boss} no Canal {channel + 1}!")

        # Quando o tempo acaba, atualizar o estado e o histórico
        if self.timers_per_boss[boss]['timers'][channel] <= 0:
            timer.stop()
            label.setText('Boss Vivo!')
            label.setStyleSheet("color: black;")
            self.update_history(f"Boss {boss} no Canal {channel + 1} renasceu!")
            self.save_state()

    def show_alert(self, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setText(message)
        msg.setWindowTitle("Alerta")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    def update_history(self, event):
        # Atualizar o histórico com o último evento no topo
        current_text = self.history_content.text()
        self.history_content.setText(f"{event}\n{current_text}")

    def clear_history(self):
        # Limpar o histórico
        self.history_content.setText("Histórico de eventos:")

    def save_state(self):
        state = {}
        for boss in self.boss_names:
            state[boss] = {
                'timers': self.timers_per_boss[boss]['timers']
            }
        with open("timers_state.json", "w") as file:
            json.dump(state, file)

    def load_state(self):
        try:
            with open("timers_state.json", "r") as file:
                state = json.load(file)
                for boss in self.boss_names:
                    for i in range(8):
                        self.timers_per_boss[boss]['timers'][i] = state[boss]['timers'][i]
                        # Se o timer ainda está ativo, reiniciar a contagem
                        if state[boss]['timers'][i] > 0:
                            self.start_timer(i, boss, state[boss]['timers'][i])
        except FileNotFoundError:
            pass

# Inicializar o aplicativo
app = QApplication(sys.argv)
tracker = BossTracker()
tracker.show()
sys.exit(app.exec_())  # Mantém o loop de eventos do PyQt5 rodando
