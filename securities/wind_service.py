# securities/wind_service.py

from WindPy import w
import logging
from django.conf import settings
import datetime
from decimal import Decimal

logger = logging.getLogger(__name__)

# 在模块加载时启动 WindPy
if not w.isconnected():
    w.start(waitTime=60)
    if not w.isconnected():
        logger.error("WindPy启动失败！")
    else:
        logger.info("WindPy已成功启动！")

# Mock data for testing
MOCK_BOND_DATA = {
    "242697.SH": {
        "issuer": "乌鲁木齐经济技术开发区建发国有资本投资运营（集团）有限公司",
        "issue_date": "2020-01-15",
        "term": "5Y",
        "remaining_term": Decimal("4.8")
    },
    "123456.SH": {
        "issuer": "上海浦东发展银行",
        "issue_date": "2021-03-20",
        "term": "3Y",
        "remaining_term": Decimal("2.5")
    },
    "789012.SH": {
        "issuer": "中国建设银行",
        "issue_date": "2022-06-10",
        "term": "2Y",
        "remaining_term": Decimal("1.8")
    }
}

def get_bond_info_by_code(bond_code):
    """
    模拟通过债券Wind代码获取债券信息
    """
    logger.info(f"Mock Wind API call for bond code: {bond_code}")
    
    if bond_code in MOCK_BOND_DATA:
        return MOCK_BOND_DATA[bond_code]
    else:
        logger.warning(f"Bond code {bond_code} not found in mock data")
        return None

def get_bond_info_by_abbr(bond_abbr):
    """
    模拟通过债券简称查询债券信息
    """
    logger.info(f"Mock Wind API call for bond abbreviation: {bond_abbr}")
    
    # For simplicity, we'll just return the first matching bond
    for code, data in MOCK_BOND_DATA.items():
        if bond_abbr.lower() in data["issuer"].lower():
            return {**data, "bond_code": code}
    
    logger.warning(f"No bond found matching abbreviation: {bond_abbr}")
    return None

def shutdown_wind():
    """
    模拟关闭Wind连接
    """
    logger.info("Mock Wind API shutdown")
