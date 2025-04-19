import csv
import random
from datetime import datetime, timedelta
from decimal import Decimal
from django.core.management.base import BaseCommand
from securities.models import Issuer, Bond, Fund, FundCompany, BondHolding, Person
from django.utils import timezone

class Command(BaseCommand):
    help = 'Imports mock bond data into the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before importing',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing data...')
            Person.objects.all().delete()
            BondHolding.objects.all().delete()
            Bond.objects.all().delete()
            Issuer.objects.all().delete()
            Fund.objects.all().delete()
            FundCompany.objects.all().delete()
            
        self.stdout.write('Importing mock data...')
        
        # Create issuers
        issuers_data = [
            {"name": "中国建设银行", "other_info": "信用评级: AAA, 行业: 银行"},
            {"name": "上海浦东发展银行", "other_info": "信用评级: AAA, 行业: 银行"},
            {"name": "中国石油天然气集团有限公司", "other_info": "信用评级: AAA, 行业: 能源"},
            {"name": "阿里巴巴集团", "other_info": "信用评级: AA+, 行业: 互联网"},
            {"name": "腾讯控股有限公司", "other_info": "信用评级: AA+, 行业: 互联网"},
            {"name": "华为技术有限公司", "other_info": "信用评级: AA+, 行业: 通信"},
            {"name": "万科企业股份有限公司", "other_info": "信用评级: AA, 行业: 房地产"},
            {"name": "中国铁路工程集团有限公司", "other_info": "信用评级: AAA, 行业: 基建"},
            {"name": "乌鲁木齐经济技术开发区建发国有资本投资运营（集团）有限公司", "other_info": "信用评级: AA-, 行业: 基建"},
            {"name": "宁德时代新能源科技股份有限公司", "other_info": "信用评级: AA+, 行业: 新能源"}
        ]
        
        issuers = {}
        for issuer_data in issuers_data:
            issuer, created = Issuer.objects.get_or_create(
                issuer_name=issuer_data["name"],
                defaults={
                    "other_info": issuer_data["other_info"]
                }
            )
            issuers[issuer_data["name"]] = issuer
            if created:
                self.stdout.write(f'Created issuer: {issuer.issuer_name}')
        
        # Create bonds
        bonds_data = [
            {"code": "220501.IB", "issuer": "中国建设银行", "term_years": 5, "issue_date": "2022-05-01"},
            {"code": "210310.IB", "issuer": "上海浦东发展银行", "term_years": 3, "issue_date": "2021-03-10"},
            {"code": "230215.IB", "issuer": "中国石油天然气集团有限公司", "term_years": 7, "issue_date": "2023-02-15"},
            {"code": "220712.IB", "issuer": "阿里巴巴集团", "term_years": 5, "issue_date": "2022-07-12"},
            {"code": "210605.IB", "issuer": "腾讯控股有限公司", "term_years": 3, "issue_date": "2021-06-05"},
            {"code": "220917.IB", "issuer": "华为技术有限公司", "term_years": 10, "issue_date": "2022-09-17"},
            {"code": "210429.IB", "issuer": "万科企业股份有限公司", "term_years": 3, "issue_date": "2021-04-29"},
            {"code": "190708.IB", "issuer": "中国铁路工程集团有限公司", "term_years": 5, "issue_date": "2019-07-08"},
            {"code": "200115.IB", "issuer": "乌鲁木齐经济技术开发区建发国有资本投资运营（集团）有限公司", "term_years": 5, "issue_date": "2020-01-15"},
            {"code": "220331.IB", "issuer": "宁德时代新能源科技股份有限公司", "term_years": 5, "issue_date": "2022-03-31"},
            {"code": "242697.SH", "issuer": "乌鲁木齐经济技术开发区建发国有资本投资运营（集团）有限公司", "term_years": 5, "issue_date": "2020-01-15"},
            {"code": "123456.SH", "issuer": "上海浦东发展银行", "term_years": 3, "issue_date": "2021-03-20"},
            {"code": "789012.SH", "issuer": "中国建设银行", "term_years": 2, "issue_date": "2022-06-10"}
        ]
        
        bonds = {}
        for bond_data in bonds_data:
            issue_date = datetime.strptime(bond_data["issue_date"], "%Y-%m-%d").date()
            
            name = f"{bond_data['issuer']}债券{bond_data['issue_date'][-5:]}"
            other_attributes = f"Name: {name}, Bond type: 公司债, Coupon Rate: {random.uniform(2.5, 5.5):.2f}%"
            
            bond, created = Bond.objects.get_or_create(
                bond_code=bond_data["code"],
                defaults={
                    "issuer": issuers[bond_data["issuer"]],
                    "term_years": bond_data["term_years"],
                    "issue_date": issue_date,
                    "other_attributes": other_attributes
                }
            )
            bonds[bond_data["code"]] = bond
            if created:
                self.stdout.write(f'Created bond: {bond.bond_code}')
        
        # Create fund companies
        fund_companies_data = [
            {"name": "华夏基金管理有限公司", "aum": "10000000000", "company_type": "FUND"},
            {"name": "易方达基金管理有限公司", "aum": "12000000000", "company_type": "FUND"},
            {"name": "南方基金管理有限公司", "aum": "9500000000", "company_type": "FUND"},
            {"name": "博时基金管理有限公司", "aum": "8500000000", "company_type": "FUND"},
            {"name": "嘉实基金管理有限公司", "aum": "11000000000", "company_type": "FUND"}
        ]
        
        fund_companies = {}
        for fund_company_data in fund_companies_data:
            fund_company, created = FundCompany.objects.get_or_create(
                company_name=fund_company_data["name"],
                defaults={
                    "aum": Decimal(fund_company_data["aum"]),
                    "company_type": fund_company_data["company_type"]
                }
            )
            fund_companies[fund_company_data["name"]] = fund_company
            if created:
                self.stdout.write(f'Created fund company: {fund_company.company_name}')
        
        # Create funds
        funds_data = [
            {"name": "华夏债券精选", "company": "华夏基金管理有限公司", "manager": "张明"},
            {"name": "华夏收益债券", "company": "华夏基金管理有限公司", "manager": "李涛"},
            {"name": "易方达稳健收益债券", "company": "易方达基金管理有限公司", "manager": "王强"},
            {"name": "易方达增强回报债券", "company": "易方达基金管理有限公司", "manager": "刘华"},
            {"name": "南方宝元债券", "company": "南方基金管理有限公司", "manager": "吴天"},
            {"name": "南方多元债券", "company": "南方基金管理有限公司", "manager": "赵佳"},
            {"name": "博时宏观回报债券", "company": "博时基金管理有限公司", "manager": "陈明"},
            {"name": "博时信用债券", "company": "博时基金管理有限公司", "manager": "黄志"},
            {"name": "嘉实债券", "company": "嘉实基金管理有限公司", "manager": "周亮"},
            {"name": "嘉实稳固收益债券", "company": "嘉实基金管理有限公司", "manager": "许洁"}
        ]
        
        funds = {}
        for fund_data in funds_data:
            fund, created = Fund.objects.get_or_create(
                fund_name=fund_data["name"],
                defaults={
                    "fund_company": fund_companies[fund_data["company"]],
                    "fund_manager": fund_data["manager"]
                }
            )
            funds[fund_data["name"]] = fund
            if created:
                self.stdout.write(f'Created fund: {fund.fund_name}')
        
        # Create persons (fund managers and traders)
        persons_data = [
            {"name": "张明", "role": "基金经理", "fund": "华夏债券精选", "is_primary": True, "phone": "13800001111", "email": "zhangming@huaxia.com"},
            {"name": "李涛", "role": "基金经理", "fund": "华夏收益债券", "is_primary": True, "phone": "13800002222", "email": "litao@huaxia.com"},
            {"name": "王强", "role": "基金经理", "fund": "易方达稳健收益债券", "is_primary": True, "phone": "13800003333", "email": "wangqiang@efunds.com"},
            {"name": "刘华", "role": "基金经理", "fund": "易方达增强回报债券", "is_primary": True, "phone": "13800004444", "email": "liuhua@efunds.com"},
            {"name": "吴天", "role": "基金经理", "fund": "南方宝元债券", "is_primary": True, "phone": "13800005555", "email": "wutian@southernfund.com"},
            {"name": "赵佳", "role": "基金经理", "fund": "南方多元债券", "is_primary": True, "phone": "13800006666", "email": "zhaojia@southernfund.com"},
            {"name": "陈明", "role": "基金经理", "fund": "博时宏观回报债券", "is_primary": True, "phone": "13800007777", "email": "chenming@bosera.com"},
            {"name": "黄志", "role": "基金经理", "fund": "博时信用债券", "is_primary": True, "phone": "13800008888", "email": "huangzhi@bosera.com"},
            {"name": "周亮", "role": "基金经理", "fund": "嘉实债券", "is_primary": True, "phone": "13800009999", "email": "zhouliang@jsfund.com"},
            {"name": "许洁", "role": "基金经理", "fund": "嘉实稳固收益债券", "is_primary": True, "phone": "13800000000", "email": "xujie@jsfund.com"},
            {"name": "张三", "role": "交易员", "fund": "华夏债券精选", "is_primary": False, "phone": "13900001111", "email": "zhangsan@huaxia.com"},
            {"name": "李四", "role": "交易员", "fund": "华夏收益债券", "is_primary": False, "phone": "13900002222", "email": "lisi@huaxia.com"},
            {"name": "王五", "role": "交易员", "fund": "易方达稳健收益债券", "is_primary": False, "phone": "13900003333", "email": "wangwu@efunds.com"},
            {"name": "赵六", "role": "交易员", "fund": "易方达增强回报债券", "is_primary": False, "phone": "13900004444", "email": "zhaoliu@efunds.com"},
            {"name": "孙七", "role": "交易员", "fund": "南方宝元债券", "is_primary": False, "phone": "13900005555", "email": "sunqi@southernfund.com"}
        ]
        
        for person_data in persons_data:
            person, created = Person.objects.get_or_create(
                name=person_data["name"],
                fund=funds[person_data["fund"]],
                defaults={
                    "role": person_data["role"],
                    "is_primary": person_data["is_primary"],
                    "phone": person_data["phone"],
                    "email": person_data["email"]
                }
            )
            if created:
                self.stdout.write(f'Created person: {person.name} ({person.role})')
        
        # Create bond holdings
        # Define which funds hold which bonds
        holdings_data = [
            {"fund": "华夏债券精选", "bond": "220501.IB", "amount": "50000000", "percentage": "5.2"},
            {"fund": "华夏债券精选", "bond": "210310.IB", "amount": "40000000", "percentage": "4.1"},
            {"fund": "华夏收益债券", "bond": "220501.IB", "amount": "30000000", "percentage": "3.5"},
            {"fund": "华夏收益债券", "bond": "230215.IB", "amount": "35000000", "percentage": "4.0"},
            {"fund": "易方达稳健收益债券", "bond": "210310.IB", "amount": "60000000", "percentage": "6.5"},
            {"fund": "易方达稳健收益债券", "bond": "220712.IB", "amount": "45000000", "percentage": "4.8"},
            {"fund": "易方达增强回报债券", "bond": "210605.IB", "amount": "55000000", "percentage": "5.8"},
            {"fund": "易方达增强回报债券", "bond": "220917.IB", "amount": "40000000", "percentage": "4.2"},
            {"fund": "南方宝元债券", "bond": "210429.IB", "amount": "35000000", "percentage": "3.7"},
            {"fund": "南方宝元债券", "bond": "190708.IB", "amount": "25000000", "percentage": "2.6"},
            {"fund": "南方多元债券", "bond": "200115.IB", "amount": "30000000", "percentage": "3.2"},
            {"fund": "南方多元债券", "bond": "220331.IB", "amount": "45000000", "percentage": "4.7"},
            {"fund": "博时宏观回报债券", "bond": "220501.IB", "amount": "50000000", "percentage": "5.3"},
            {"fund": "博时宏观回报债券", "bond": "220712.IB", "amount": "40000000", "percentage": "4.2"},
            {"fund": "博时信用债券", "bond": "210605.IB", "amount": "35000000", "percentage": "3.7"},
            {"fund": "博时信用债券", "bond": "220917.IB", "amount": "45000000", "percentage": "4.8"},
            {"fund": "嘉实债券", "bond": "190708.IB", "amount": "30000000", "percentage": "3.1"},
            {"fund": "嘉实债券", "bond": "200115.IB", "amount": "35000000", "percentage": "3.6"},
            {"fund": "嘉实稳固收益债券", "bond": "220331.IB", "amount": "40000000", "percentage": "4.1"},
            {"fund": "嘉实稳固收益债券", "bond": "210429.IB", "amount": "30000000", "percentage": "3.1"}
        ]
        
        for holding_data in holdings_data:
            holding, created = BondHolding.objects.get_or_create(
                fund=funds[holding_data["fund"]],
                bond=bonds[holding_data["bond"]],
                defaults={
                    "holding_amount": Decimal(holding_data["amount"]),
                    "holding_percentage": Decimal(holding_data["percentage"])
                }
            )
            if created:
                self.stdout.write(f'Created bond holding: {holding.fund.fund_name} - {holding.bond.bond_code}')
        
        self.stdout.write(self.style.SUCCESS('Successfully imported mock data!')) 