import os

class GeneradorMapa:
    @staticmethod
    def crear_mapa_delivery(lat_origen=10.0488, lng_origen=-66.8282, lat_destino=10.0588, lng_destino=-66.8182, ruta_salida="data/mapa.html"):
        contenido_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Mapa MoveGo Delivery</title>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <style>
        html, body, #map {{ height: 100%; margin: 0; padding: 0; }}
    </style>
</head>
<body>
    <div id="map"></div>
    <script>
        var map = L.map('map').setView([{lat_origen}, {lng_origen}], 13);
        
        L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
            maxZoom: 19,
            attribution: '© OpenStreetMap'
        }}).addTo(map);

        // Marcador Origen (Conductor / Salida)
        L.marker([{lat_origen}, {lng_origen}]).addTo(map)
            .bindPopup('Punto de Origen / Repartidor')
            .openPopup();

        // Marcador Destino (Entrega)
        L.marker([{lat_destino}, {lng_destino}]).addTo(map)
            .bindPopup('Punto de Destino / Cliente');

        // Línea de ruta entre ambos puntos
        var latlngs = [
            [{lat_origen}, {lng_origen}],
            [{lat_destino}, {lng_destino}]
        ];
        var polyline = L.polyline(latlngs, {{color: 'blue', weight: 4, opacity: 0.7}}).addTo(map);
        map.fitBounds(polyline.getBounds(), {{padding: [30, 30]}});
    </script>
</body>
</html>"""
        
        directorio = os.path.dirname(ruta_salida)
        if directorio and not os.path.exists(directorio):
            os.makedirs(directorio)
            
        with open(ruta_salida, "w", encoding="utf-8") as f:
            f.write(contenido_html)
            
        return ruta_salida

    @staticmethod
    def crear_mapa_html(latitud=-33.4489, longitud=-70.6693, ruta_salida="data/mapa.html"):
        return GeneradorMapa.crear_mapa_delivery(latitud, longitud, latitud, longitud, ruta_salida)