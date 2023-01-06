from app.database import BaseDb
from flask import Blueprint, request
from flask import current_app
bp = Blueprint('db', __name__, url_prefix="/db")
db = BaseDb()
from app.database import global_config
import logging
logger = logging.getLogger(__name__)
REDIS_KEY = global_config.get('redis', 'REDIS_KEY')


@bp.route('/pushAppData', methods=['post'])
# 分区写入数据
def push_app():
    try:
        data = request.get_json()
        _id = data.pop('_id')
        keys = data['source']
        seen_fenqu = db.appinfo_seen(keys, _id)
        seen_total = db.appinfo_seen(REDIS_KEY, _id)
        if seen_total:
            db.insert_mongo(data, _id)
            current_app.logger.info('入库数据id:{}'.format(_id))
            return {
                'code': 200,
                'msg': '成功'
            }
        return {
            'code': 200,
            'msg': '数据已存在'
        }
    except Exception as e:
        current_app.logger.error(e)
        return {
            'code': 400,
            'msg': '{}'.format(e)
        }

@bp.route('/popAppData', methods=['get'])
# 分区取数据
def pop_app():
    try:
        name = request.args.get('name')
        number = request.args.get('number')
        area = request.args.get('area')
        city = request.args.get('city')
        province = request.args.get('province')
        current_app.logger.info('name:{}, number:{}, area:{}, city:{}, province:{}'.format(name, number, area, city, province))
        logger.info('name:{}, number:{}, area:{}, city:{}, province:{}'.format(name, number, area, city, province))
        sets = db.get_setdiff(name, number, area, city, province)
        data = db.get_mongo_datas(sets,  name)
        return {
            'code': 200,
            'msg': '成功',
            'data': data
        }
    except Exception as e:
        current_app.logger.error(e)
        return {
            'code': 400,
            'msg': '{}'.format(e)
        }

@bp.route('/monitorAppData', methods=['post'])
# 数据指标
def monitor_app():
    try:
        data = request.get_json()
        data = db.insert_mongos(data, data["_id"])
        current_app.logger.info('{}'.format(data))
        return {
            'code': 200,
            'msg': '成功',
            'data': data
        }
    except Exception as e:
        current_app.logger.error(e)
        return {
            'code': 400,
            'msg': '{}'.format(e)
        }

@bp.route('/test', methods=['get'])
def test():
    """
	测试
	"""
    return "ok"