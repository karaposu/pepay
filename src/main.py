
import logging
logger = logging.getLogger(__name__)
import sys
from app import app


if __name__ == "__main__":
    import uvicorn
    # uvicorn.run(app, host="0.0.0.0", port=8000)
    uvicorn.run(app, host="0.0.0.0", port=3000, log_level="debug")



 # ssl_certfile = "/home/enes/ssl/combined_certificate.crt"
 #    ssl_keyfile = "/home/enes/ssl/budgety_ai.key"
 #
 #    # Run the FastAPI app with SSL on port 443
 #    uvicorn.run(
 #        "app:app",  # Assuming your FastAPI app is defined in main.py
 #        host="0.0.0.0",
 #        port=443,  # Port 443 for HTTPS
 #        log_level="debug",
 #        ssl_certfile=ssl_certfile,  # Path to the SSL certificate
 #        ssl_keyfile=ssl_keyfile     # Path to the SSL private key
 #    )