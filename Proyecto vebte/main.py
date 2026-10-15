import sys
import os
from PyQt5.QtWidgets import QApplication
from models.gestor import GestorVehiculos
from views.main_window import VentanaPrincipal


def cargar_estilos(app: QApplication, ruta_qcss: str) -> None:
    if os.path.exists(ruta_qcss):
        with open(ruta_qcss, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())


def main():
    app = QApplication(sys.argv)
    
    # Cargar hoja de estilos QCSS
    cargar_estilos(app, "styles/style.qcss")

    # Inicializar modelo y vista
    gestor = GestorVehiculos(ruta_archivo="data/vehiculos.json")
    ventana = VentanaPrincipal(gestor)
    ventana.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()