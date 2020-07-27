""" Main project file, used to run it. """

from app import app
from config import Config


if __name__ == "__main__":
	app.run(host=Config.WEBHOOK_LISTEN,
			port=Config.WEBHOOK_PORT,
			ssl_context=(Config.WEBHOOK_SSL_CERT, Config.WEBHOOK_SSL_PRIV),
			debug=Config.DEBUG)
