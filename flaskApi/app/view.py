from app.database import BaseDb
from flask import Blueprint, request
from flask import current_app
from ..settings import REDIS_KEY
# import logging
# logger = logging.getLogger(__name__)
bp = Blueprint('db', __name__, url_prefix="/db")
db = BaseDb()

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
            'msg': '已存在'
        }
    except Exception as e:
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
        number = number if number else 5
        sets = db.get_setdiff(name, REDIS_KEY)
        data = db.get_mongo_datas(sets, number)
        return {
            'code': 200,
            'msg': '成功',
            'data': data
        }
    except Exception as e:
        return {
            'code': 400,
            'msg': '{}'.format(e)
        }

@bp.route('/test', methods=['get'])
def test():
    """
	测试redis
	"""
    current_app.logger.info('wIUGEHF')
    return "ok"