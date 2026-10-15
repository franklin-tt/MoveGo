import os
import qrcode


class GeneradorQR:
    @staticmethod
    def generar_qr_delivery(
        id_envio: str, lat: float, lng: float, ruta_salida: str = "data/qr_delivery.png"
    ) -> str:
        url_maps = f"https://www.google.com/maps/search/?api=1&query={lat},{lng}"
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(url_maps)
        qr.make(fit=True)

        img = qr.make_image(fill_color="#FF5E36", back_color="white")
        directorio = os.path.dirname(ruta_salida)
        if directorio and not os.path.exists(directorio):
            os.makedirs(directorio)

        img.save(ruta_salida)
        return ruta_salida