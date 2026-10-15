import os
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QLineEdit, QTextEdit, QComboBox, QMessageBox, QDoubleSpinBox
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl
from models.mapa_generator import GeneradorMapa
from models.qr_generator import GeneradorQR

class VistaDeliveryMapaChat(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        main_layout = QHBoxLayout(self)

        # Panel Izquierdo: Mapa GPS (Leaflet / Estilo Google Maps)
        left_layout = QVBoxLayout()
        title_mapa = QLabel("MoveGO - Rastreo GPS en Vivo")
        title_mapa.setStyleSheet("font-weight: bold; font-size: 14px; color: white;")
        left_layout.addWidget(title_mapa)

        self.web_view = QWebEngineView()
        left_layout.addWidget(self.web_view)

        # Panel Central: Chat de Servicio
        chat_layout = QVBoxLayout()
        title_chat = QLabel("Chat de Servicio MoveGO")
        title_chat.setStyleSheet("font-weight: bold; font-size: 14px; color: white;")
        chat_layout.addWidget(title_chat)

        self.txt_chat_history = QTextEdit()
        self.txt_chat_history.setReadOnly(True)
        chat_layout.addWidget(self.txt_chat_history)

        chat_input_layout = QHBoxLayout()
        self.input_msg = QLineEdit()
        self.input_msg.setPlaceholderText("Escribe un mensaje al conductor...")
        btn_send = QPushButton("Enviar")
        btn_send.clicked.connect(self.enviar_mensaje)
        chat_input_layout.addWidget(self.input_msg)
        chat_input_layout.addWidget(btn_send)

        chat_layout.addLayout(chat_input_layout)

        # Panel Derecho: Simulación de Ruta, Cálculo por Distancia y Pago QR
        right_layout = QVBoxLayout()
        title_ops = QLabel("Gestión de Tarifa & QR")
        title_ops.setStyleSheet("font-weight: bold; font-size: 14px; color: white;")
        right_layout.addWidget(title_ops)

        right_layout.addWidget(QLabel("Selecciona Servicio:"))
        self.combo_servicio = QComboBox()
        self.combo_servicio.addItems(["Carro", "Moto", "Delivery"])
        self.combo_servicio.currentIndexChanged.connect(self.calcular_y_actualizar)
        right_layout.addWidget(self.combo_servicio)

        self.input_origen = QLineEdit()
        self.input_origen.setPlaceholderText("Lugar de Origen...")
        right_layout.addWidget(self.input_origen)

        self.input_destino = QLineEdit()
        self.input_destino.setPlaceholderText("Lugar de Destino...")
        right_layout.addWidget(self.input_destino)

        right_layout.addWidget(QLabel("Distancia estimada (km):"))
        self.spin_distancia = QDoubleSpinBox()
        self.spin_distancia.setRange(0.5, 500.0)
        self.spin_distancia.setValue(5.0)
        self.spin_distancia.valueChanged.connect(self.calcular_y_actualizar)
        right_layout.addWidget(self.spin_distancia)

        btn_simular = QPushButton("Actualizar Mapa y Calcular")
        btn_simular.clicked.connect(self.cargar_mapa)
        right_layout.addWidget(btn_simular)

        self.lbl_monto = QLabel("Monto Estimado: $0.00 USD")
        self.lbl_monto.setStyleSheet("font-weight: bold; font-size: 15px; color: #FF5E36;")
        right_layout.addWidget(self.lbl_monto)

        self.combo_pago = QComboBox()
        self.combo_pago.addItems(["Pago Móvil", "Zelle", "Efectivo"])
        right_layout.addWidget(self.combo_pago)

        btn_confirmar = QPushButton("Confirmar Pago / QR")
        btn_confirmar.clicked.connect(self.confirmar_pago)
        right_layout.addWidget(btn_confirmar)

        # Unir Todo en el Layout Principal
        main_layout.addLayout(left_layout, stretch=3)
        main_layout.addLayout(chat_layout, stretch=2)
        main_layout.addLayout(right_layout, stretch=2)

        # Calcular monto inicial y cargar mapa
        self.calcular_y_actualizar()
        self.cargar_mapa()

    def calcular_tarifa_viaje(self, tipo_servicio: str, distancia_km: float) -> float:
        """Calcula el costo total del viaje basado en la distancia y el tipo de transporte."""
        tarifas_base = {
            "Carro": {"inicio": 2.0, "por_km": 1.2},
            "Moto": {"inicio": 1.0, "por_km": 0.8},
            "Delivery": {"inicio": 1.5, "por_km": 1.0}
        }
        
        config = tarifas_base.get(tipo_servicio, {"inicio": 1.5, "por_km": 1.0})
        total = config["inicio"] + (distancia_km * config["por_km"])
        return round(total, 2)

    def calcular_y_actualizar(self):
        tipo = self.combo_servicio.currentText()
        distancia = self.spin_distancia.value()
        total = self.calcular_tarifa_viaje(tipo, distancia)
        self.lbl_monto.setText(f"Monto Estimado: ${total:.2f} USD")

    def cargar_mapa(self):
        origen = self.input_origen.text().strip()
        destino = self.input_destino.text().strip()
        distancia = self.spin_distancia.value()
        tipo = self.combo_servicio.currentText()
        total = self.calcular_tarifa_viaje(tipo, distancia)
        
        lat_o, lng_o = 10.0488, -66.8282
        lat_d, lng_d = 10.0588, -66.8182

        ruta_relativa = GeneradorMapa.crear_mapa_delivery(lat_o, lng_o, lat_d, lng_d)
        ruta_absoluta = os.path.abspath(ruta_relativa)
        self.web_view.setUrl(QUrl.fromLocalFile(ruta_absoluta))
        
        GeneradorQR.generar_qr_delivery("MOV-001", lat_d, lng_d)

        if origen and destino:
            self.txt_chat_history.append(f"<b>Sistema:</b> Solicitud de [{tipo}] creada de <i>{origen}</i> a <i>{destino}</i> ({distancia} km). Total a pagar: <b>${total:.2f} USD</b>.")
        else:
            self.txt_chat_history.append(f"<b>Sistema:</b> Mapa actualizado. Tipo: {tipo} | Distancia: {distancia} km | Tarifa: ${total:.2f} USD.")

    def enviar_mensaje(self):
        texto = self.input_msg.text().strip()
        if texto:
            self.txt_chat_history.append(f"<b>Tú:</b> {texto}")
            self.input_msg.clear()
            self.txt_chat_history.append("<b>Conductor:</b> ¡Entendido! Voy en camino.")

    def confirmar_pago(self):
        metodo = self.combo_pago.currentText()
        tipo = self.combo_servicio.currentText()
        distancia = self.spin_distancia.value()
        total = self.calcular_tarifa_viaje(tipo, distancia)
        
        QMessageBox.information(self, "Pago Exitoso", f"¡Pago de ${total:.2f} procesado mediante {metodo} con éxito! Viaje registrado en MoveGO.")
        self.txt_chat_history.append(f"<b>Sistema:</b> Pago confirmado de ${total:.2f} vía {metodo}. ¡Gracias por viajar con MoveGO!")