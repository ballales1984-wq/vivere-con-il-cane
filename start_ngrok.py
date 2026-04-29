#!/usr/bin/env python3
"""
Persistent ngrok tunnel manager with auto-reconnect
"""
import time
import signal
import sys
from pyngrok import ngrok, conf
import logging

# Configura logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def handle_shutdown(signum, frame):
    """Gestisce lo shutdown pulito"""
    logger.info("Shutting down ngrok tunnel...")
    ngrok.disconnect()
    ngrok.kill()
    sys.exit(0)

def main():
    # Registra i segnali per shutdown pulito
    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)

    # Configura ngrok (usa eventuale authtoken da variabile d'ambiente o file)
    # NGROK_AUTHTOKEN può essere impostato in .env o come variabile d'ambiente
    import os
    authtoken = os.environ.get("NGROK_AUTHTOKEN", "")
    if authtoken:
        ngrok.set_auth_token(authtoken)
        logger.info("Ngrok authtoken configured")
    else:
        logger.warning("No NGROK_AUTHTOKEN found - using free tier (unstable, random URL)")

    # Kill eventuali istanze ngrok residue
    ngrok.kill()

    # Avvia il tunnel verso Django
    tunnel = None
    while True:
    try:
        logger.info("Starting ngrok tunnel to http://localhost:8000")
        # Usa --pooling-enabled per permettere più sessioni sullo stesso dominio (se presente)
        # Se hai un dominio riservato, usa: 
        # tunnel = ngrok.connect(8000, "tonita-deposable-manneristically.ngrok-free.dev", pooling_enabled=True)
        # Altrimenti usa un tunnel casuale:
        tunnel = ngrok.connect(8000, pooling_enabled=True)
        logger.info(f"Tunnel created: {tunnel.public_url}")

            # Mantieni attivo
            while tunnel and tunnel.proc:
                time.sleep(5)
                if not tunnel.proc.poll() is None:
                    logger.warning("Ngrok process terminated, restarting...")
                    break

        except Exception as e:
            logger.error(f"Error: {e}, retrying in 10 seconds...")
            time.sleep(10)

if __name__ == "__main__":
    main()
