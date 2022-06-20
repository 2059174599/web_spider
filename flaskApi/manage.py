from flask import Flask
from app.view import bp
import logging
from logging.handlers import TimedRotatingFileHandler



app = Flask(__name__)
# 注册接口
app.register_blueprint(bp)


if __name__=="__main__":
	formatter = logging.Formatter(

		"[%(asctime)s][%(filename)s:%(lineno)d][%(levelname)s][%(thread)d] - %(message)s")

	handler = TimedRotatingFileHandler(

		"logs/flask.log", when="D", interval=1, backupCount=15,

		encoding="UTF-8", delay=False, utc=True)

	app.logger.addHandler(handler)

	handler.setFormatter(formatter)
	app.logger.info('iwuegyu')
	app.run(debug=True)