from flask import Flask
from app.view import bp
import logging
from logging.handlers import TimedRotatingFileHandler



app = Flask(__name__)
# 注册接口
app.register_blueprint(bp)


if __name__=="__main__":
	app.run(host='0.0.0.0', port=8090)