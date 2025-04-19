from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import IntegrityError
from decimal import Decimal
from securities.models import Issuer, Bond, FundCompany, Fund, Person, BondHolding
import datetime

class Command(BaseCommand):
    help = 'Adds sample data for testing bond matching'

    def handle(self, *args, **kwargs):
        # Create sample issuers
        issuer_data = [
            {"name": "中国建设银行", "info": "国有六大行之一"},
            {"name": "中国工商银行", "info": "国有六大行之一"},
            {"name": "中国银行", "info": "国有六大行之一"},
            {"name": "中国农业银行", "info": "国有六大行之一"},
            {"name": "中国邮政储蓄银行", "info": "国有六大行之一"},
            {"name": "交通银行", "info": "国有六大行之一"}
        ]
        
        for data in issuer_data:
            issuer, created = Issuer.objects.get_or_create(
                issuer_name=data["name"],
                defaults={"other_info": data["info"]}
            )
            if created:
                self.stdout.write(f"Created issuer: {issuer.issuer_name}")
            else:
                self.stdout.write(f"Issuer already exists: {issuer.issuer_name}")
        
        # Create sample fund companies
        company_data = [
            {"name": "嘉实基金管理有限公司", "type": "FUND", "contact": "010-12345678", "aum": Decimal("800000000000.00")},
            {"name": "易方达基金管理有限公司", "type": "FUND", "contact": "020-12345678", "aum": Decimal("900000000000.00")},
            {"name": "博时基金管理有限公司", "type": "FUND", "contact": "021-12345678", "aum": Decimal("700000000000.00")},
            {"name": "华夏基金管理有限公司", "type": "FUND", "contact": "010-87654321", "aum": Decimal("850000000000.00")},
            {"name": "南方基金管理有限公司", "type": "FUND", "contact": "0755-12345678", "aum": Decimal("750000000000.00")},
        ]
        
        for data in company_data:
            company, created = FundCompany.objects.get_or_create(
                company_name=data["name"],
                defaults={
                    "company_type": data["type"],
                    "contact_info": data["contact"],
                    "aum": data["aum"]
                }
            )
            if created:
                self.stdout.write(f"Created fund company: {company.company_name}")
            else:
                self.stdout.write(f"Fund company already exists: {company.company_name}")
        
        # Create sample funds
        fund_data = [
            {"company": "嘉实基金管理有限公司", "name": "嘉实纯债债券型基金", "manager": "王明", "email": "wangming@jsfund.com", "phone": "13800138000"},
            {"company": "嘉实基金管理有限公司", "name": "嘉实信用债券型基金", "manager": "张华", "email": "zhanghua@jsfund.com", "phone": "13800138001"},
            {"company": "易方达基金管理有限公司", "name": "易方达双债增强债券型基金", "manager": "李伟", "email": "liwei@efunds.com", "phone": "13900139000"},
            {"company": "博时基金管理有限公司", "name": "博时信用债券投资基金", "manager": "赵静", "email": "zhaojing@bosera.com", "phone": "13800138002"},
            {"company": "华夏基金管理有限公司", "name": "华夏债券型证券投资基金", "manager": "陈刚", "email": "chengang@chinaamc.com", "phone": "13800138003"},
            {"company": "南方基金管理有限公司", "name": "南方宝元债券型基金", "manager": "刘强", "email": "liuqiang@southernfund.com", "phone": "13800138004"},
        ]
        
        for data in fund_data:
            try:
                company = FundCompany.objects.get(company_name=data["company"])
                fund, created = Fund.objects.get_or_create(
                    fund_company=company,
                    fund_name=data["name"],
                    defaults={
                        "fund_manager": data["manager"],
                        "contact_email": data["email"],
                        "contact_phone": data["phone"]
                    }
                )
                if created:
                    self.stdout.write(f"Created fund: {fund.fund_name}")
                    
                    # Create persons for each fund
                    try:
                        # Create fund manager
                        Person.objects.create(
                            fund=fund,
                            name=data["manager"],
                            role="基金经理",
                            phone=data["phone"],
                            email=data["email"],
                            is_primary=True
                        )
                        
                        # Create trader
                        Person.objects.create(
                            fund=fund,
                            name=f"交易员-{data['manager'][:1]}",
                            role="交易员",
                            phone=f"135{data['phone'][3:]}",
                            email=f"trader_{data['email']}",
                            is_primary=False
                        )
                        
                        self.stdout.write(f"Added persons for fund: {fund.fund_name}")
                    except IntegrityError:
                        self.stdout.write(f"Person already exists for fund: {fund.fund_name}")
                else:
                    self.stdout.write(f"Fund already exists: {fund.fund_name}")
            except FundCompany.DoesNotExist:
                self.stdout.write(f"Error: Fund company not found: {data['company']}")
        
        # Get China Construction Bank issuer
        try:
            ccb_issuer = Issuer.objects.get(issuer_name="中国建设银行")
            
            # Create bonds
            bond_data = [
                {"code": "220501.IB", "issue_date": "2022-05-01", "term": Decimal("5.00"), "remaining": Decimal("3.8"), "coupon": "3.25%", "name": "22建行债05-01"},
                {"code": "190708.IB", "issue_date": "2019-07-08", "term": Decimal("5.00"), "remaining": Decimal("0.0"), "coupon": "3.85%", "name": "19铁路债"},
                {"code": "789012.SH", "issue_date": "2022-06-10", "term": Decimal("2.00"), "remaining": Decimal("0.9"), "coupon": "2.95%", "name": "22建行债"},
            ]
            
            bonds = []
            for data in bond_data:
                try:
                    bond = Bond.objects.get(bond_code=data["code"])
                    self.stdout.write(f"Bond already exists: {bond.bond_code}")
                    bonds.append(bond)
                except Bond.DoesNotExist:
                    issue_date = datetime.datetime.strptime(data["issue_date"], "%Y-%m-%d").date()
                    bond = Bond.objects.create(
                        issuer=ccb_issuer,
                        bond_code=data["code"],
                        issue_date=issue_date,
                        term_years=data["term"],
                        remaining_term=data["remaining"],
                        other_attributes=f"Name: {data['name']}, Bond type: 公司债, Coupon Rate: {data['coupon']}"
                    )
                    self.stdout.write(f"Created bond: {bond.bond_code}")
                    bonds.append(bond)
                
            # Add holdings for the first 3 funds
            funds = Fund.objects.all()[:3]
            
            for fund in funds:
                for bond in bonds:
                    try:
                        # First check if the holding already exists
                        purchase_date = bond.issue_date + datetime.timedelta(days=30)
                        holding = BondHolding.objects.get(
                            fund=fund,
                            bond=bond,
                            purchase_date=purchase_date
                        )
                        self.stdout.write(f"Bond holding already exists: {fund.fund_name} - {bond.bond_code}")
                    except BondHolding.DoesNotExist:
                        # Create a new holding if it doesn't exist
                        holding = BondHolding.objects.create(
                            fund=fund,
                            bond=bond,
                            purchase_date=purchase_date,
                            remaining_term_at_purchase=bond.remaining_term + Decimal("0.1"),
                            holding_amount=Decimal("100000000.00"),  # 1亿元
                            holding_percentage=Decimal("5.00"),  # 5%
                            is_current_holding=True if bond.remaining_term > 0 else False
                        )
                        self.stdout.write(f"Created bond holding: {fund.fund_name} - {bond.bond_code}")
                
        except Issuer.DoesNotExist:
            self.stdout.write(self.style.ERROR("Error: China Construction Bank issuer not found"))
        
        self.stdout.write(self.style.SUCCESS("Successfully added sample data")) 