from flask import Blueprint, request
from flask import current_app
from app.database import BaseDb
BD = BaseDb()
monitory = Blueprint('app', __name__, url_prefix="/app")



@monitory.route('/spider', methods=['post'])
# 数据指标
def monitor_spider():
    try:
        sour_data = request.get_json()
        sour_data = BD.checkData(sour_data)
        data = BD.getData(sour_data)
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

@monitory.route('/down', methods=['post'])
# 数据指标
def monitor_down():
    try:
        sour_data = request.get_json()
        sour_data = BD.checkData(sour_data)
        data = BD.getData(sour_data, 'appDownloadNum')
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