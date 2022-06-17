from flask import Flask
from app.view import bp
import logging
import logging.handlers
from flask.logging import default_handler


# 创建handler(日志处理器), 指定了输出路径
# file_handler = logging.FileHandler(log_file_path, encoding='UTF-8')
file_handler = logging.handlers.TimedRotatingFileHandler("logs/flask.log", when="D", interval=1, backupCount=3)
stream_handler = logging.StreamHandler()
# 设置日志输出格式
formatter = logging.Formatter(
	fmt="%(asctime)s %(levelname)s %(filename)s %(funcName)s[line:%(lineno)d] %(message)s",
	datefmt="%Y-%m-%d %X"
)
# 为handler(处理器)指定输出的日志格式
file_handler.setFormatter(formatter)
stream_handler.setFormatter(formatter)
# 为handler(处理器)指定终端输出的日志等级,即只有级别大于等于logging.WARNING的日志才会在终端输出
file_handler.setLevel(logging.INFO)
stream_handler.setLevel(logging.INFO)


app = Flask(__name__)
# app.config['REDIS_HOST'] = "127.0.0.1" # redis数据库地址
# app.config['REDIS_PORT'] = 6379 # redis 端口号
# app.config['REDIS_DB'] = 0 # 数据库名
# app.config['REDIS_EXPIRE'] = 60 # redis 过期时间60秒
# 注册接口
app.logger.addHandler(file_handler)
app.logger.addHandler(stream_handler)
app.register_blueprint(bp)


if __name__=="__main__":
	app.run(debug=True)