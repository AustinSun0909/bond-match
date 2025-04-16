# securities/wind_service.py

from WindPy import w
import logging
from django.conf import settings
import datetime

logger = logging.getLogger(__name__)

# 在模块加载时启动 WindPy
if not w.isconnected():
    w.start(waitTime=60)
    if not w.isconnected():
        logger.error("WindPy启动失败！")
    else:
        logger.info("WindPy已成功启动！")

def get_bond_info_by_code(bond_code):
    """
    通过债券Wind代码获取债券的发行主体、发行时间和期限。
    参数:
      bond_code: str, 如 "102123456.IB" 或其他正确Wind代码
    返回:
      如果成功，返回包含“issuer”、“issuebegin”、“term”的字典；否则返回 None。
    """
    # 这里使用w.wss接口获取截面数据，例如：
    fields = "issuer,issuebegin,term"
    result = w.wss(bond_code, fields)
    if result.ErrorCode != 0:
        logger.error(f"Wind查询失败，错误码: {result.ErrorCode}")
        return None
    try:
        # 注意result.Data中每个字段返回的是列表（假设只取一条记录）
        issuer = result.Data[0][0]
        issuebegin = result.Data[1][0]
        term = result.Data[2][0]
        # 如果issuebegin是日期对象，则可以格式化
        if isinstance(issuebegin, datetime.date):
            issuebegin = issuebegin.strftime("%Y-%m-%d")
        return {
            "issuer": issuer,
            "issuebegin": issuebegin,
            "term": term
        }
    except Exception as e:
        logger.exception(f"解析Wind数据时出错: {e}")
        return None

def get_bond_info_by_abbr(bond_abbr):
    """
    通过债券简称查询债券Wind代码，再进一步获取债券发行信息。
    这种方法有两种实现思路：
      1. 如果 Wind API 支持按简称直接筛选（如通过w.wset进行查询），则可利用w.wset接口；
      2. 或者你已经在本地维护了债券简称与Wind代码的映射表。
    下面我们以使用 Wind 命令生成器辅助生成的w.wset为例。
    """
    # 这里的示例假设Wind命令生成器生成的命令类似如下：
    # 注意：请根据实际Wind API的参数和字段调整
    wset_result = w.wset("bondbasicinfo", f"bond_abbr={bond_abbr};field=wind_code,issuer,issuebegin,term")
    if wset_result.ErrorCode != 0:
        logger.error(f"Wind查询（简称）失败，错误码: {wset_result.ErrorCode}")
        return None
    try:
        # 假设返回的数据分别为：wind_code, issuer, issuebegin, term
        # 这里我们只取第一个结果记录
        wind_code = wset_result.Data[0][0]
        issuer = wset_result.Data[1][0]
        issuebegin = wset_result.Data[2][0]
        term = wset_result.Data[3][0]
        if isinstance(issuebegin, datetime.date):
            issuebegin = issuebegin.strftime("%Y-%m-%d")
        return {
            "wind_code": wind_code,
            "issuer": issuer,
            "issuebegin": issuebegin,
            "term": term
        }
    except Exception as e:
        logger.exception(f"解析Wind简称查询数据出错: {e}")
        return None

def shutdown_wind():
    """
    程序退出前调用，关闭WindPy连接。
    """
    try:
        w.stop()
        logger.info("WindPy已停止。")
    except Exception as e:
        logger.exception(f"关闭WindPy时出错: {e}")
