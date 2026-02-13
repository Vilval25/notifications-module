"""
Script simple para probar la API REST
Ejecutar con: python test_api.py
(Asegúrate de tener el servidor corriendo: python app.py)
"""

import requests
import json


BASE_URL = "http://localhost:5000"


def test_health():
    """Prueba el endpoint de salud"""
    print("\n" + "="*60)
    print("TEST: Health Check")
    print("="*60)

    response = requests.get(f"{BASE_URL}/health")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")


def test_send_email():
    """Prueba enviar un email"""
    print("\n" + "="*60)
    print("TEST: Enviar Email")
    print("="*60)

    payload = {
        "recipient": "gustavo.vila@unmsm.edu.pe",
        "channel": "email",
        "template_name": "welcome",
        "params": {
            "name": "Juan Pérez",
            "source_module": "TEST_API"
        }
    }

    print(f"Payload: {json.dumps(payload, indent=2)}")

    response = requests.post(f"{BASE_URL}/api/notifications/send", json=payload)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")


def test_get_logs():
    """Prueba obtener los logs"""
    print("\n" + "="*60)
    print("TEST: Obtener Logs")
    print("="*60)

    response = requests.get(f"{BASE_URL}/api/notifications/logs?limit=5")
    print(f"Status Code: {response.status_code}")
    data = response.json()
    print(f"Total logs: {data.get('total', 0)}")
    print(f"Logs: {json.dumps(data, indent=2)}")


def main():
    """Ejecuta todas las pruebas"""
    print("\n🚀 Iniciando pruebas de la API de Notificaciones...")
    print("Asegúrate de que el servidor esté corriendo: python app.py\n")

    try:
        # Prueba 1: Health check
        test_health()

        # Prueba 2: Enviar email
        test_send_email()

        # Prueba 3: Obtener logs
        test_get_logs()

        print("\n" + "="*60)
        print("✅ Todas las pruebas completadas")
        print("="*60)

    except requests.exceptions.ConnectionError:
        print("\n❌ Error: No se pudo conectar al servidor")
        print("Asegúrate de ejecutar primero: python app.py")
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()
