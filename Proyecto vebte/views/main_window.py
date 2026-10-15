import os
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QLineEdit, QComboBox, QMessageBox, 
    QStackedWidget, QTextEdit, QDoubleSpinBox, QTableWidget, 
    QTableWidgetItem, QHeaderView, QGroupBox, QProgressBar, QSpinBox,
    QInputDialog
)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl
from models.mapa_generator import GeneradorMapa
from models.qr_generator import GeneradorQR
from models.gestor import GestorVehiculos
from models.carro import Carro
from models.moto import Moto


class VentanaPrincipal(QMainWindow):
    def __init__(self, gestor: GestorVehiculos):
        super().__init__()
        self._gestor = gestor
        self.setWindowTitle("MoveGO - Movilidad & Delivery")
        self.resize(1280, 800)
        
        # Estado del viaje y telemetría
        self.estado_viaje = "Inactivo"
        self.viaje_actual = None

        # Diccionario para almacenar las calificaciones y reseñas escritas por los usuarios
        # Formato: {"ABC-123": {"estrellas": "5.0", "resenas": ["Excelente servicio", "Muy puntual"]}}
        self.calificaciones_conductores = {}

        # Timer para simular el trayecto y el consumo de combustible en vivo
        self.timer_simulacion = QTimer()
        self.timer_simulacion.timeout.connect(self._actualizar_progreso_viaje)
        self.tanque_gasolina_actual = 100.0
        
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        self._init_pantalla_seleccion_rol()
        self._init_pantalla_cliente()
        self._init_pantalla_conductor()
        
        self.stacked_widget.setCurrentIndex(0)

    # -------------------------------------------------------------------
    # PANTALLA 0: SELECCIÓN DE ROL
    # -------------------------------------------------------------------
    def _init_pantalla_seleccion_rol(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignCenter)
        
        lbl_logo = QLabel("MoveGO 🚀")
        lbl_logo.setStyleSheet("font-size: 42px; font-weight: bold; color: #FF5E36; margin-bottom: 5px;")
        lbl_logo.setAlignment(Qt.AlignCenter)
        
        lbl_slogan = QLabel("Tu plataforma de transporte y delivery al instante")
        lbl_slogan.setStyleSheet("font-size: 14px; color: #8C9BAE; margin-bottom: 40px;")
        lbl_slogan.setAlignment(Qt.AlignCenter)
        
        btn_cliente = QPushButton("👤 Entrar como Usuario / Pasajero")
        btn_cliente.setStyleSheet("background-color: #FF5E36; color: white; font-weight: bold; font-size: 14px; padding: 14px 28px; border-radius: 10px;")
        btn_cliente.setFixedWidth(350)
        btn_cliente.setCursor(Qt.PointingHandCursor)
        btn_cliente.clicked.connect(self._abrir_pantalla_cliente)
        
        btn_conductor = QPushButton("🚗 Panel de Conductor / Registrar Unidad")
        btn_conductor.setStyleSheet("background-color: #242A35; color: white; font-weight: bold; font-size: 14px; padding: 14px 28px; border-radius: 10px; border: 1px solid #3A4454;")
        btn_conductor.setFixedWidth(350)
        btn_conductor.setCursor(Qt.PointingHandCursor)
        btn_conductor.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(2))
        
        layout.addWidget(lbl_logo)
        layout.addWidget(lbl_slogan)
        layout.addWidget(btn_cliente, alignment=Qt.AlignCenter)
        layout.addSpacing(15)
        layout.addWidget(btn_conductor, alignment=Qt.AlignCenter)
        
        self.stacked_widget.addWidget(page)

    # -------------------------------------------------------------------
    # PANTALLA 1: PASAJERO (SELECCIÓN DE CONDUCTOR CON ESTRELLAS NARANJAS)
    # -------------------------------------------------------------------
    def _init_pantalla_cliente(self):
        page = QWidget()
        main_layout = QHBoxLayout(page)

        # Izquierda: Mapa GPS y Telemetría de Combustible
        left_layout = QVBoxLayout()
        header_mapa = QHBoxLayout()
        btn_volver_1 = QPushButton("← Menú Principal")
        btn_volver_1.setFixedWidth(130)
        btn_volver_1.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        header_mapa.addWidget(btn_volver_1)
        header_mapa.addWidget(QLabel("<b>🗺️ Mapa de Ruta en Vivo</b>"))
        header_mapa.addStretch()
        left_layout.addLayout(header_mapa)

        self.web_view = QWebEngineView()
        left_layout.addWidget(self.web_view)

        # Telemetría de Gasolina / Batería
        group_sim = QGroupBox("⛽ Nivel de Combustible / Gasolina de la Unidad")
        layout_sim = QVBoxLayout(group_sim)
        self.lbl_estado_viaje = QLabel("Estado: Esperando selección de viaje...")
        self.lbl_estado_viaje.setStyleSheet("font-weight: bold; color: #00D084;")
        layout_sim.addWidget(self.lbl_estado_viaje)
        
        self.progress_bar_gasolina = QProgressBar()
        self.progress_bar_gasolina.setValue(100)
        layout_sim.addWidget(self.progress_bar_gasolina)
        left_layout.addWidget(group_sim)

        # Centro: Chat de Servicio y Reseñas del Conductor seleccionado
        center_layout = QVBoxLayout()
        center_layout.addWidget(QLabel("<b>💬 Chat con el Conductor</b>"))
        
        self.txt_chat_history = QTextEdit()
        self.txt_chat_history.setReadOnly(True)
        self.txt_chat_history.append("<b>Sistema:</b> Bienvenido a MoveGO. Elige un conductor para ver sus reseñas.")
        center_layout.addWidget(self.txt_chat_history)

        chat_input_layout = QHBoxLayout()
        self.input_msg = QLineEdit()
        self.input_msg.setPlaceholderText("Escribe un mensaje al conductor...")
        btn_send = QPushButton("Enviar")
        btn_send.clicked.connect(self.enviar_mensaje_cliente)
        chat_input_layout.addWidget(self.input_msg)
        chat_input_layout.addWidget(btn_send)
        center_layout.addLayout(chat_input_layout)

        # Panel para ver reseñas del conductor con estrellas naranjas
        center_layout.addWidget(QLabel("<b><span style='color: #FF5E36;'>★</span> Reseñas de la comunidad sobre este Conductor:</b>"))
        self.txt_resenas_conductor = QTextEdit()
        self.txt_resenas_conductor.setReadOnly(True)
        self.txt_resenas_conductor.setMaximumHeight(120)
        self.txt_resenas_conductor.append("Selecciona un conductor arriba para ver lo que opinan los pasajeros.")
        center_layout.addWidget(self.txt_resenas_conductor)

        # Derecha: Elección de Conductor, Distancia y Detalle de Tarifa
        right_layout = QVBoxLayout()
        right_layout.addWidget(QLabel("<b>📦 Solicitar Carrera</b>"))

        right_layout.addWidget(QLabel("Elige tu Conductor:"))
        self.combo_conductores_disponibles = QComboBox()
        self.combo_conductores_disponibles.currentIndexChanged.connect(self.actualizar_panel_resenas_cliente)
        right_layout.addWidget(self.combo_conductores_disponibles)

        right_layout.addWidget(QLabel("Tipo de Servicio:"))
        self.combo_servicio = QComboBox()
        self.combo_servicio.addItems(["Carro 🚗", "Moto 🏍️", "Delivery 📦"])
        self.combo_servicio.currentIndexChanged.connect(self.calcular_y_actualizar)
        right_layout.addWidget(self.combo_servicio)

        self.input_origen = QLineEdit()
        self.input_origen.setPlaceholderText("Lugar de Origen")
        right_layout.addWidget(self.input_origen)

        self.input_destino = QLineEdit()
        self.input_destino.setPlaceholderText("Lugar de Destino")
        right_layout.addWidget(self.input_destino)

        right_layout.addWidget(QLabel("Distancia del viaje (km):"))
        self.spin_distancia = QDoubleSpinBox()
        self.spin_distancia.setRange(0.5, 500.0)
        self.spin_distancia.setValue(5.0)
        self.spin_distancia.valueChanged.connect(self.calcular_y_actualizar)
        right_layout.addWidget(self.spin_distancia)

        self.lbl_detalle_gasolina = QLabel("Gasolina requerida: 0.50 L")
        self.lbl_detalle_gasolina.setStyleSheet("color: #8C9BAE; font-size: 12px;")
        right_layout.addWidget(self.lbl_detalle_gasolina)

        self.lbl_monto = QLabel("Monto Total a Pagar: $0.00 USD")
        self.lbl_monto.setStyleSheet("font-weight: bold; font-size: 15px; color: #FF5E36; margin-top: 5px;")
        right_layout.addWidget(self.lbl_monto)

        btn_iniciar_carrera = QPushButton("🚀 Iniciar Carrera con este Conductor")
        btn_iniciar_carrera.setStyleSheet("background-color: #FF5E36; color: white; font-weight: bold; padding: 12px; border-radius: 6px;")
        btn_iniciar_carrera.clicked.connect(self.iniciar_carrera_pasajero)
        right_layout.addWidget(btn_iniciar_carrera)

        right_layout.addWidget(QLabel("Método de Pago:"))
        self.combo_pago = QComboBox()
        self.combo_pago.addItems(["Pago Móvil", "Zelle", "Efectivo"])
        right_layout.addWidget(self.combo_pago)

        btn_confirmar_pago = QPushButton("💳 Pagar Carrera y Dejar Reseña")
        btn_confirmar_pago.clicked.connect(self.confirmar_pago_viaje)
        right_layout.addWidget(btn_confirmar_pago)

        main_layout.addLayout(left_layout, stretch=3)
        main_layout.addLayout(center_layout, stretch=2)
        main_layout.addLayout(right_layout, stretch=2)

        self.stacked_widget.addWidget(page)
        self.calcular_y_actualizar()
        self.cargar_mapa_inicial()

    # -------------------------------------------------------------------
    # PANTALLA 2: PANEL DE CONDUCTOR (GESTIÓN Y BORRADO DE UNIDADES)
    # -------------------------------------------------------------------
    def _init_pantalla_conductor(self):
        page = QWidget()
        layout_principal = QHBoxLayout(page)

        layout_izq = QVBoxLayout()
        header_driver = QHBoxLayout()
        btn_volver_2 = QPushButton("← Menú Principal")
        btn_volver_2.setFixedWidth(130)
        btn_volver_2.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        header_driver.addWidget(btn_volver_2)
        header_driver.addWidget(QLabel("<b>🚗 Panel del Conductor / Gestión de Unidades</b>"))
        header_driver.addStretch()
        layout_izq.addLayout(header_driver)

        grupo_registro = QGroupBox("Registrar / Modificar Unidad")
        form_layout = QVBoxLayout(grupo_registro)

        form_layout.addWidget(QLabel("Tipo de Unidad:"))
        self.combo_tipo_veh = QComboBox()
        self.combo_tipo_veh.addItems(["Carro", "Moto"])
        form_layout.addWidget(self.combo_tipo_veh)

        self.txt_placa = QLineEdit()
        self.txt_placa.setPlaceholderText("Placa / ID (Ej: ABC-123)")
        form_layout.addWidget(self.txt_placa)

        self.txt_marca = QLineEdit()
        self.txt_marca.setPlaceholderText("Marca (Ej: Toyota, Honda)")
        form_layout.addWidget(self.txt_marca)

        self.txt_modelo = QLineEdit()
        self.txt_modelo.setPlaceholderText("Modelo")
        form_layout.addWidget(self.txt_modelo)

        btn_registrar = QPushButton("Guardar / Registrar Unidad")
        btn_registrar.clicked.connect(self.registrar_vehiculo_conductor)
        form_layout.addWidget(btn_registrar)
        layout_izq.addWidget(grupo_registro)

        layout_izq.addWidget(QLabel("<b>Mis Unidades Registradas en MoveGO:</b>"))
        self.tabla_vehiculos = QTableWidget()
        self.tabla_vehiculos.setColumnCount(5)
        self.tabla_vehiculos.setHorizontalHeaderLabels(["Placa/ID", "Tipo", "Marca", "Modelo", "Reputación"])
        self.tabla_vehiculos.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout_izq.addWidget(self.tabla_vehiculos)

        # Botón para eliminar vehículos de la lista
        btn_eliminar_vehiculo = QPushButton("🗑️ Eliminar Unidad Seleccionada")
        btn_eliminar_vehiculo.setStyleSheet("background-color: #D9534F; color: white; font-weight: bold; padding: 10px; border-radius: 6px;")
        btn_eliminar_vehiculo.clicked.connect(self.eliminar_vehiculo_conductor)
        layout_izq.addWidget(btn_eliminar_vehiculo)

        layout_principal.addLayout(layout_izq, stretch=1)
        self.stacked_widget.addWidget(page)
        self.actualizar_tabla_vehiculos()

    # -------------------------------------------------------------------
    # LÓGICA Y FUNCIONALIDADES
    # -------------------------------------------------------------------
    def _abrir_pantalla_cliente(self):
        self.actualizar_combo_conductores()
        self.stacked_widget.setCurrentIndex(1)

    def actualizar_combo_conductores(self):
        self.combo_conductores_disponibles.clear()
        vehiculos = self._gestor.listar_todos()
        if not vehiculos:
            self.combo_conductores_disponibles.addItem("No hay conductores registrados")
        else:
            for v in vehiculos:
                info = self.calificaciones_conductores.get(v.id, {"estrellas": "5.0", "resenas": []})
                estrellas_html = "<span style='color: #FF5E36; font-weight: bold;'>★★★★★</span>"
                self.combo_conductores_disponibles.addItem(f"{v.obtener_tipo()} - {v.marca} {v.modelo} [{v.id}] | {estrellas_html} ({info['estrellas']})")
        self.actualizar_panel_resenas_cliente()

    def actualizar_panel_resenas_cliente(self):
        conductor_sel = self.combo_conductores_disponibles.currentText()
        if "No hay conductores" in conductor_sel or not conductor_sel:
            self.txt_resenas_conductor.setText("No hay conductores disponibles para mostrar reseñas.")
            return

        v_id = conductor_sel.split("[")[-1].split("]")[0] if "[" in conductor_sel else ""
        info = self.calificaciones_conductores.get(v_id, {"estrellas": "5.0", "resenas": ["Sin reseñas previas. ¡Sé el primero en calificarlo!"]})
        
        estrellas_pintadas = "<span style='color: #FF5E36; font-size: 14px;'>★★★★★</span>"
        
        texto_resenas = f"<b>Calificación Global:</b> {estrellas_pintadas} ({info['estrellas']})<br><br><b>Opiniones de pasajeros:</b><br>"
        for r in info["resenas"]:
            texto_resenas += f"• \"{r}\"<br>"
        if not info["resenas"]:
            texto_resenas += "• <i>Aún no hay comentarios escritos.</i>"

        self.txt_resenas_conductor.setHtml(texto_resenas)

    def calcular_tarifa(self, tipo: str, km: float) -> tuple:
        tarifas = {
            "Carro 🚗": {"base": 2.0, "km": 1.2, "cons_gas_km": 0.10},
            "Moto 🏍️": {"base": 1.0, "km": 0.8, "cons_gas_km": 0.05},
            "Delivery 📦": {"base": 1.5, "km": 1.0, "cons_gas_km": 0.07}
        }
        cfg = tarifas.get(tipo, {"base": 1.5, "km": 1.0, "cons_gas_km": 0.08})
        monto_total = round(cfg["base"] + (km * cfg["km"]), 2)
        gasolina_usada = round(km * cfg["cons_gas_km"], 2)
        return monto_total, gasolina_usada

    def calcular_y_actualizar(self):
        tipo = self.combo_servicio.currentText()
        km = self.spin_distancia.value()
        total, gas_usada = self.calcular_tarifa(tipo, km)
        self.lbl_monto.setText(f"Monto Total a Pagar: ${total:.2f} USD")
        self.lbl_detalle_gasolina.setText(f"⛽ Gasolina consumida estimada: {gas_usada:.2f} Litros")

    def cargar_mapa_inicial(self):
        ruta = GeneradorMapa.crear_mapa_delivery(10.0488, -66.8282, 10.0588, -66.8182)
        self.web_view.setUrl(QUrl.fromLocalFile(os.path.abspath(ruta)))

    def iniciar_carrera_pasajero(self):
        import random
        
        conductor_sel = self.combo_conductores_disponibles.currentText()
        if "No hay conductores" in conductor_sel or not conductor_sel:
            QMessageBox.warning(self, "Sin Conductor", "Primero debes registrar una unidad en el Panel de Conductor.")
            return

        origen = self.input_origen.text().strip()
        destino = self.input_destino.text().strip()
        if not origen or not destino:
            QMessageBox.warning(self, "Campos Incompletos", "Por favor ingresa dirección de origen y destino.")
            return

        tipo = self.combo_servicio.currentText()
        km = self.spin_distancia.value()
        total, gas_usada = self.calcular_tarifa(tipo, km)

        v_id = conductor_sel.split("[")[-1].split("]")[0] if "[" in conductor_sel else "CONDUCTOR"

        if "Carro" in tipo:
            gasto_visual = (km * 8.0) + random.randint(-4, 4)
        elif "Moto" in tipo:
            gasto_visual = (km * 3.5) + random.randint(-2, 2)
        else:
            gasto_visual = (km * 5.5) + random.randint(-3, 3)

        porcentaje_consumo = min(90, max(10, int(gasto_visual)))

        self.viaje_actual = {
            "conductor_str": conductor_sel,
            "v_id": v_id,
            "origen": origen,
            "destino": destino,
            "km": km,
            "total": total,
            "gasolina_usada": gas_usada,
            "consumo_porcentaje": porcentaje_consumo
        }

        self.cargar_mapa_inicial()
        GeneradorQR.generar_qr_delivery("MOV-CARRERA", 10.0588, -66.8182)

        self.estado_viaje = "En progreso"
        self.tanque_gasolina_actual = 100.0
        self.progress_bar_gasolina.setValue(100)
        
        self.nivel_objetivo = 100 - porcentaje_consumo
        
        self.lbl_estado_viaje.setText(f"Estado: 🚗 Consumo de {gas_usada}L en {km} km ({tipo})...")
        self.timer_simulacion.start(150)

        self.txt_chat_history.append(
            f"<b>Sistema:</b> Carrera iniciada con éxito.<br>"
            f"• Servicio: <b>{tipo}</b> | Ruta: <i>{origen}</i> ➔ <i>{destino}</i> ({km} km)<br>"
            f"• Consumo estimado: <b>{gas_usada} Litros</b> (La barra bajará un {porcentaje_consumo}%).<br>"
            f"• Tarifa para el conductor: <b>${total:.2f} USD</b>."
        )

    def _actualizar_progreso_viaje(self):
        if self.tanque_gasolina_actual > self.nivel_objetivo:
            self.tanque_gasolina_actual -= 2.0
            self.progress_bar_gasolina.setValue(int(self.tanque_gasolina_actual))
        else:
            self.timer_simulacion.stop()
            self.estado_viaje = "Finalizado"
            self.lbl_estado_viaje.setText("Estado: ✅ ¡Destino alcanzado! Carrera finalizada.")
            self.txt_chat_history.append("<b>Sistema:</b> ¡Llegaron al destino! El viaje ha finalizado. Procede con el pago y deja tu reseña.")

    def registrar_vehiculo_conductor(self):
        v_id = self.txt_placa.text().strip().upper()
        marca = self.txt_marca.text().strip()
        modelo = self.txt_modelo.text().strip()
        tipo = self.combo_tipo_veh.currentText()

        if not v_id or not marca or not modelo:
            QMessageBox.warning(self, "Campos Vacíos", "Por favor completa todos los datos de la unidad.")
            return

        if v_id not in self.calificaciones_conductores:
            self.calificaciones_conductores[v_id] = {"estrellas": "5.0", "resenas": []}

        obj = Carro(v_id, marca, modelo, 2023, 120.0, num_puertas=4) if tipo == "Carro" else Moto(v_id, marca, modelo, 2023, 100.0, cilindraje=150)

        if self._gestor.agregar_vehiculo(obj):
            self.actualizar_tabla_vehiculos()
            self.actualizar_combo_conductores()
            self.txt_placa.clear()
            self.txt_marca.clear()
            self.txt_modelo.clear()
            QMessageBox.information(self, "¡Éxito!", "Unidad registrada correctamente.")
        else:
            QMessageBox.warning(self, "Error", "La placa o ID ya existe.")

    def eliminar_vehiculo_conductor(self):
        fila = self.tabla_vehiculos.currentRow()
        if fila < 0:
            QMessageBox.warning(self, "Selección Requerida", "Por favor selecciona un vehículo de la tabla para eliminar.")
            return

        v_id = self.tabla_vehiculos.item(fila, 0).text()
        confirm = QMessageBox.question(
            self, 
            "Confirmar Borrado", 
            f"¿Estás seguro de que deseas eliminar la unidad con placa/ID '{v_id}'?",
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )

        if confirm == QMessageBox.Yes:
            if self._gestor.eliminar_vehiculo(v_id):
                if v_id in self.calificaciones_conductores:
                    del self.calificaciones_conductores[v_id]
                self.actualizar_tabla_vehiculos()
                self.actualizar_combo_conductores()
                QMessageBox.information(self, "Eliminado", f"La unidad '{v_id}' ha sido eliminada con éxito.")
            else:
                QMessageBox.warning(self, "Error", "No se pudo eliminar el vehículo.")

    def actualizar_tabla_vehiculos(self):
        vehiculos = self._gestor.listar_todos()
        self.tabla_vehiculos.setRowCount(len(vehiculos))
        for fila, v in enumerate(vehiculos):
            info = self.calificaciones_conductores.get(v.id, {"estrellas": "5.0", "resenas": []})
            
            self.tabla_vehiculos.setItem(fila, 0, QTableWidgetItem(v.id))
            self.tabla_vehiculos.setItem(fila, 1, QTableWidgetItem(v.obtener_tipo()))
            self.tabla_vehiculos.setItem(fila, 2, QTableWidgetItem(v.marca))
            self.tabla_vehiculos.setItem(fila, 3, QTableWidgetItem(v.modelo))
            
            item_estrellas = QTableWidgetItem(f"★ ({info['estrellas']})")
            self.tabla_vehiculos.setItem(fila, 4, item_estrellas)

    def enviar_mensaje_cliente(self):
        msg = self.input_msg.text().strip()
        if msg:
            self.txt_chat_history.append(f"<b>Tú:</b> {msg}")
            self.input_msg.clear()
            self.txt_chat_history.append("<b>Conductor:</b> ¡Entendido, voy atento al camino!")

    def confirmar_pago_viaje(self):
        if self.estado_viaje != "Finalizado":
            QMessageBox.warning(self, "Pago Rechazado ❌", "¡El pago ha rebotado! No puedes pagar la carrera hasta que el viaje haya finalizado por completo.")
            self.txt_chat_history.append("<b>Sistema:</b> Pago rebotado. Espera a que la carrera termine.")
            return

        metodo = self.combo_pago.currentText()
        total = self.viaje_actual["total"] if self.viaje_actual else 0.0
        v_id = self.viaje_actual.get("v_id", "") if self.viaje_actual else ""

        puntuacion, ok_puntos = QInputDialog.getItem(
            self, 
            "Calificar Conductor", 
            f"¡Pago de ${total:.2f} USD procesado vía {metodo}!\n\nSelecciona las estrellas para este servicio:", 
            [
                "5 Estrellas (<span style='color: #FF5E36;'>★★★★★</span> Excelente)", 
                "4 Estrellas (<span style='color: #FF5E36;'>★★★★</span> Bueno)", 
                "3 Estrellas (<span style='color: #FF5E36;'>★★★</span> Regular)", 
                "2 Estrellas (<span style='color: #FF5E36;'>★★</span> Malo)", 
                "1 Estrella (<span style='color: #FF5E36;'>★</span> Pésimo)"
            ], 
            0, 
            False
        )

        if ok_puntos:
            resena_texto, ok_texto = QInputDialog.getText(
                self, 
                "Escribir Reseña", 
                "Escribe un comentario/reseña para el conductor:"
            )

            num_estrellas = puntuacion.split(" ")[0]
            estrellas_str = f"{num_estrellas}.0"
            
            if v_id:
                if v_id not in self.calificaciones_conductores:
                    self.calificaciones_conductores[v_id] = {"estrellas": estrellas_str, "resenas": []}
                else:
                    self.calificaciones_conductores[v_id]["estrellas"] = estrellas_str
                
                if ok_texto and resena_texto.strip():
                    self.calificaciones_conductores[v_id]["resenas"].append(resena_texto.strip())

            self.actualizar_tabla_vehiculos()
            self.actualizar_combo_conductores()

            comentario_final = resena_texto.strip() if (ok_texto and resena_texto.strip()) else "Sin comentario"
            QMessageBox.information(
                self, 
                "¡Reseña Registrada!", 
                f"¡Gracias por tu opinión!\n\nCalificación: {estrellas_str} Estrellas\nReseña: \"{comentario_final}\""
            )
            self.txt_chat_history.append(f"<b>Sistema:</b> Pago confirmado (${total:.2f} USD). Reseña enviada: <i>\"{comentario_final}\"</i> ({estrellas_str} Estrellas).")
        
        self.estado_viaje = "Inactivo"
        self.viaje_actual = None