# securities/wind_service.py

import logging
from django.conf import settings
import datetime
from decimal import Decimal
from django.utils import timezone

logger = logging.getLogger(__name__)

# Mock WindPy connection
class MockWindPy:
    def __init__(self):
        self.connected = False
    
    def isconnected(self):
        return self.connected
    
    def start(self, waitTime=60):
        logger.info("Starting mock WindPy")
        self.connected = True
        return True
    
    def close(self):
        logger.info("Closing mock WindPy")
        self.connected = False
        return True

# Create mock instance
w = MockWindPy()
w.start()

# Mock data for testing
MOCK_BOND_DATA = {
    # Original codes
    "242697.SH": {
        "bond_code": "242697.SH",
        "bond_name": "20乌经开债",
        "issuer": "乌鲁木齐经济技术开发区建发国有资本投资运营（集团）有限公司",
        "issue_date": "2020-01-15",
        "maturity_date": "2025-01-15",
        "term": "5Y",
        "term_years": "5.00",
        "remaining_term": "1.50",
        "coupon_rate": "4.35",
        "can_be_redeemed": False
    },
    "123456.SH": {
        "bond_code": "123456.SH",
        "bond_name": "21浦发银行债",
        "issuer": "上海浦东发展银行",
        "issue_date": "2021-03-20",
        "maturity_date": "2024-03-20",
        "term": "3Y",
        "term_years": "3.00",
        "remaining_term": "0.70",
        "coupon_rate": "3.75",
        "can_be_redeemed": False
    },
    "789012.SH": {
        "bond_code": "789012.SH",
        "bond_name": "22建行债",
        "issuer": "中国建设银行",
        "issue_date": "2022-06-10",
        "maturity_date": "2024-06-10",
        "term": "2Y",
        "term_years": "2.00",
        "remaining_term": "0.90",
        "coupon_rate": "2.95",
        "can_be_redeemed": False
    },
    
    # New codes
    "220501.IB": {
        "bond_code": "220501.IB",
        "bond_name": "22建行债05-01",
        "issuer": "中国建设银行",
        "issue_date": "2022-05-01",
        "maturity_date": "2027-05-01",
        "term": "5Y",
        "term_years": "5.00",
        "remaining_term": "3.80",
        "coupon_rate": "3.25",
        "can_be_redeemed": False
    },
    "210310.IB": {
        "bond_code": "210310.IB",
        "bond_name": "21浦发债03-10",
        "issuer": "上海浦东发展银行",
        "issue_date": "2021-03-10",
        "maturity_date": "2024-03-10",
        "term": "3Y",
        "term_years": "3.00",
        "remaining_term": "0.70",
        "coupon_rate": "3.65",
        "can_be_redeemed": False
    },
    "230215.IB": {
        "bond_code": "230215.IB",
        "bond_name": "23中石油债",
        "issuer": "中国石油天然气集团有限公司",
        "issue_date": "2023-02-15",
        "maturity_date": "2030-02-15",
        "term": "7Y",
        "term_years": "7.00",
        "remaining_term": "6.60",
        "coupon_rate": "3.15",
        "can_be_redeemed": False
    },
    "220712.IB": {
        "bond_code": "220712.IB",
        "bond_name": "22阿里债",
        "issuer": "阿里巴巴集团",
        "issue_date": "2022-07-12",
        "maturity_date": "2027-07-12",
        "term": "5Y",
        "term_years": "5.00",
        "remaining_term": "4.00",
        "coupon_rate": "3.45",
        "can_be_redeemed": False
    },
    "210605.IB": {
        "bond_code": "210605.IB",
        "bond_name": "21腾讯债",
        "issuer": "腾讯控股有限公司",
        "issue_date": "2021-06-05",
        "maturity_date": "2024-06-05",
        "term": "3Y",
        "term_years": "3.00",
        "remaining_term": "1.00",
        "coupon_rate": "3.55",
        "can_be_redeemed": False
    },
    "220917.IB": {
        "bond_code": "220917.IB",
        "bond_name": "22华为债",
        "issuer": "华为技术有限公司",
        "issue_date": "2022-09-17",
        "maturity_date": "2032-09-17",
        "term": "10Y",
        "term_years": "10.00",
        "remaining_term": "9.20",
        "coupon_rate": "4.05",
        "can_be_redeemed": True
    },
    "210429.IB": {
        "bond_code": "210429.IB",
        "bond_name": "21万科债",
        "issuer": "万科企业股份有限公司",
        "issue_date": "2021-04-29",
        "maturity_date": "2024-04-29",
        "term": "3Y",
        "term_years": "3.00",
        "remaining_term": "0.80",
        "coupon_rate": "4.15",
        "can_be_redeemed": False
    },
    "190708.IB": {
        "bond_code": "190708.IB",
        "bond_name": "19铁路债",
        "issuer": "中国铁路工程集团有限公司",
        "issue_date": "2019-07-08",
        "maturity_date": "2024-07-08", 
        "term": "5Y",
        "term_years": "5.00",
        "remaining_term": "0.00",
        "coupon_rate": "3.85",
        "can_be_redeemed": True
    },
    "200115.IB": {
        "bond_code": "200115.IB",
        "bond_name": "20乌经开债",
        "issuer": "乌鲁木齐经济技术开发区建发国有资本投资运营（集团）有限公司",
        "issue_date": "2020-01-15",
        "maturity_date": "2025-01-15",
        "term": "5Y",
        "term_years": "5.00",
        "remaining_term": "1.50",
        "coupon_rate": "4.35",
        "can_be_redeemed": False
    },
    "220331.IB": {
        "bond_code": "220331.IB",
        "bond_name": "22宁德时代债",
        "issuer": "宁德时代新能源科技股份有限公司",
        "issue_date": "2022-03-31",
        "maturity_date": "2027-03-31",
        "term": "5Y",
        "term_years": "5.00",
        "remaining_term": "3.80",
        "coupon_rate": "3.75",
        "can_be_redeemed": True
    }
}

# Add remaining_days field for bonds with remaining term less than a year
for code, data in MOCK_BOND_DATA.items():
    if 'remaining_term' in data:
        term = float(data['remaining_term'].replace('年', '').replace('%', '')) if isinstance(data['remaining_term'], str) else float(data['remaining_term'])
        
        # If term is less than 1 year, add a remaining_days field
        if term < 1.0:
            data['remaining_days'] = str(int(term * 365)) + '日'
            
def get_bond_info_by_code(bond_code):
    """
    模拟通过债券Wind代码获取债券信息
    """
    logger.info(f"Mock Wind API call for bond code: {bond_code}")
    
    if bond_code in MOCK_BOND_DATA:
        # Make a copy of the data to avoid modifying the original
        bond_data = dict(MOCK_BOND_DATA[bond_code])
        
        # Ensure remaining_term is a number without the unit
        if 'remaining_term' in bond_data:
            if isinstance(bond_data['remaining_term'], str):
                # If it's a string, try to extract the numerical part
                try:
                    bond_data['remaining_term'] = bond_data['remaining_term'].replace('年', '')
                except:
                    pass
        
        # Calculate remaining days if less than 1 year and not already present
        if 'remaining_term' in bond_data and 'remaining_days' not in bond_data:
            try:
                term = float(bond_data['remaining_term'])
                if term < 1.0:
                    bond_data['remaining_days'] = str(int(term * 365)) + '日'
            except:
                pass
                    
        # Ensure coupon_rate doesn't have the % sign
        if 'coupon_rate' in bond_data and isinstance(bond_data['coupon_rate'], str):
            bond_data['coupon_rate'] = bond_data['coupon_rate'].replace('%', '')
            
        return bond_data
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
            return data
    
    logger.warning(f"No bond found matching abbreviation: {bond_abbr}")
    return None

def shutdown_wind():
    """
    模拟关闭Wind连接
    """
    logger.info("Mock Wind API shutdown")
    w.close()
