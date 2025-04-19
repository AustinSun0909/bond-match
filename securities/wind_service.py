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
    # Original codes
    "242697.SH": {
        "issuer": "乌鲁木齐经济技术开发区建发国有资本投资运营（集团）有限公司",
        "issue_date": "2020-01-15",
        "term": "5Y",
        "remaining_term": Decimal("1.5"),
        "coupon_rate": "4.35%", 
        "bond_name": "20乌经开债"
    },
    "123456.SH": {
        "issuer": "上海浦东发展银行",
        "issue_date": "2021-03-20",
        "term": "3Y",
        "remaining_term": Decimal("0.7"),
        "coupon_rate": "3.75%",
        "bond_name": "21浦发银行债"
    },
    "789012.SH": {
        "issuer": "中国建设银行",
        "issue_date": "2022-06-10",
        "term": "2Y",
        "remaining_term": Decimal("0.9"),
        "coupon_rate": "2.95%",
        "bond_name": "22建行债"
    },
    
    # New codes
    "220501.IB": {
        "issuer": "中国建设银行",
        "issue_date": "2022-05-01",
        "term": "5Y",
        "remaining_term": Decimal("3.8"),
        "coupon_rate": "3.25%",
        "bond_name": "22建行债05-01"
    },
    "210310.IB": {
        "issuer": "上海浦东发展银行",
        "issue_date": "2021-03-10",
        "term": "3Y",
        "remaining_term": Decimal("0.7"),
        "coupon_rate": "3.65%",
        "bond_name": "21浦发债03-10"
    },
    "230215.IB": {
        "issuer": "中国石油天然气集团有限公司",
        "issue_date": "2023-02-15",
        "term": "7Y",
        "remaining_term": Decimal("6.6"),
        "coupon_rate": "3.15%",
        "bond_name": "23中石油债"
    },
    "220712.IB": {
        "issuer": "阿里巴巴集团",
        "issue_date": "2022-07-12",
        "term": "5Y",
        "remaining_term": Decimal("4.0"),
        "coupon_rate": "3.45%",
        "bond_name": "22阿里债"
    },
    "210605.IB": {
        "issuer": "腾讯控股有限公司",
        "issue_date": "2021-06-05",
        "term": "3Y",
        "remaining_term": Decimal("1.0"),
        "coupon_rate": "3.55%",
        "bond_name": "21腾讯债"
    },
    "220917.IB": {
        "issuer": "华为技术有限公司",
        "issue_date": "2022-09-17",
        "term": "10Y",
        "remaining_term": Decimal("9.2"),
        "coupon_rate": "4.05%",
        "bond_name": "22华为债"
    },
    "210429.IB": {
        "issuer": "万科企业股份有限公司",
        "issue_date": "2021-04-29",
        "term": "3Y",
        "remaining_term": Decimal("0.8"),
        "coupon_rate": "4.15%",
        "bond_name": "21万科债"
    },
    "190708.IB": {
        "issuer": "中国铁路工程集团有限公司",
        "issue_date": "2019-07-08",
        "term": "5Y",
        "remaining_term": Decimal("0.0"),
        "coupon_rate": "3.85%",
        "bond_name": "19铁路债"
    },
    "200115.IB": {
        "issuer": "乌鲁木齐经济技术开发区建发国有资本投资运营（集团）有限公司",
        "issue_date": "2020-01-15",
        "term": "5Y",
        "remaining_term": Decimal("1.5"),
        "coupon_rate": "4.35%",
        "bond_name": "20乌经开债"
    },
    "220331.IB": {
        "issuer": "宁德时代新能源科技股份有限公司",
        "issue_date": "2022-03-31",
        "term": "5Y",
        "remaining_term": Decimal("3.8"),
        "coupon_rate": "3.75%",
        "bond_name": "22宁德时代债"
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
        if bond_abbr.lower() in data.get("bond_name", "").lower() or bond_abbr.lower() in data.get("issuer", "").lower():
            return {**data, "bond_code": code}
    
    logger.warning(f"No bond found matching abbreviation: {bond_abbr}")
    return None

def shutdown_wind():
    """
    模拟关闭Wind连接
    """
    logger.info("Mock Wind API shutdown")
