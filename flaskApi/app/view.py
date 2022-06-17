from app.database import BaseDb
from flask import Blueprint, request
from flask import current_app
import logging
logger = logging.getLogger(__name__)
bp = Blueprint('db', __name__, url_prefix="/db")
db = BaseDb()

@bp.route('/testMongoWrite', methods=['post'])
def test_mongo_write():
    try:
        # db = BaseDb()
        data = request.get_json()
        _id = data.pop('_id')
        seen = db.appinfo_seen(_id)
        if seen:
            db.insert_mongo(data, _id)
            current_app.logger.info('入库数据id:{}'.format(_id))
        return {
            'code': 200,
            'msg': '成功'
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
    return "ok"