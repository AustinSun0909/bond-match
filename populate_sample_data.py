import os
import django
import datetime
from decimal import Decimal

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bond_match.settings')
django.setup()

from django.contrib.auth.models import User
from django.utils import timezone
from securities.models import Issuer, Bond, FundCompany, Fund, Person, BondHolding, SearchHistory
from securities.wind_service import MOCK_BOND_DATA

def create_sample_data():
    print("Creating sample data...")
    
    # Create admin user if it doesn't exist
    if not User.objects.filter(username='admin').exists():
        user = User.objects.create_superuser('admin', 'admin@example.com', 'adminpassword')
        print("Created admin user")
    else:
        user = User.objects.get(username='admin')
        print("Admin user already exists")
    
    # Create issuers
    issuers = {}
    for bond_code, bond_data in MOCK_BOND_DATA.items():
        issuer_name = bond_data['issuer']
        if issuer_name not in issuers:
            issuer, created = Issuer.objects.get_or_create(
                issuer_name=issuer_name,
                defaults={
                    'other_info': f"Issuer information for {issuer_name}"
                }
            )
            issuers[issuer_name] = issuer
            if created:
                print(f"Created issuer: {issuer_name}")
            else:
                print(f"Issuer already exists: {issuer_name}")
    
    # Create bonds based on mock data
    bonds = {}
    for bond_code, bond_data in MOCK_BOND_DATA.items():
        issuer = issuers[bond_data['issuer']]
        
        # Parse dates
        issue_date = datetime.datetime.strptime(bond_data['issue_date'], '%Y-%m-%d').date()
        maturity_date = datetime.datetime.strptime(bond_data['maturity_date'], '%Y-%m-%d').date() if 'maturity_date' in bond_data else None
        
        # Get the bond if it exists
        existing_bond = Bond.objects.filter(bond_code=bond_code).first()
        
        if existing_bond:
            # Update the bond name if it's empty
            if not existing_bond.bond_name or existing_bond.bond_name == '':
                existing_bond.bond_name = bond_data['bond_name']
                existing_bond.save(update_fields=['bond_name'])
                print(f"Updated bond name: {bond_code} - {bond_data['bond_name']}")
            bonds[bond_code] = existing_bond
            print(f"Bond already exists: {bond_code}")
        else:
            # Create new bond
            bond = Bond.objects.create(
                bond_code=bond_code,
                issuer=issuer,
                bond_name=bond_data['bond_name'],
                issue_date=issue_date,
                maturity_date=maturity_date,
                term_years=Decimal(bond_data['term_years']),
                remaining_term=Decimal(bond_data['remaining_term']),
                coupon_rate=Decimal(bond_data['coupon_rate']),
                can_be_redeemed=bond_data.get('can_be_redeemed', False),
                other_attributes=f"Additional info for {bond_code}"
            )
            bonds[bond_code] = bond
            print(f"Created bond: {bond_code} - {bond_data['bond_name']}")
    
    # Update bonds with missing or incorrect remaining_term
    for bond_code, bond_data in MOCK_BOND_DATA.items():
        bond = Bond.objects.filter(bond_code=bond_code).first()
        if bond:
            if 'remaining_term' in bond_data:
                try:
                    # Get the numerical value
                    remaining_term = bond_data['remaining_term']
                    if isinstance(remaining_term, str):
                        remaining_term = remaining_term.replace('年', '').replace('%', '')
                    
                    # Update the bond remaining term
                    if bond.remaining_term is None or bond.remaining_term == Decimal('0.00') or bond.remaining_term != Decimal(remaining_term):
                        bond.remaining_term = Decimal(remaining_term)
                        bond.save(update_fields=['remaining_term'])
                        print(f"Updated remaining term for bond {bond_code}: {remaining_term}")
                except Exception as e:
                    print(f"Error updating remaining term for bond {bond_code}: {str(e)}")
            
            # Make sure bond name is set correctly
            if bond.bond_name != bond_data.get('bond_name', ''):
                bond.bond_name = bond_data.get('bond_name', '')
                bond.save(update_fields=['bond_name'])
                print(f"Updated bond name for {bond_code}: {bond_data.get('bond_name', '')}")
    
    # Create fund companies
    fund_companies = []
    for company_type, company_name in [
        ('FUND', '华夏基金管理有限公司'),
        ('FUND', '博时基金管理有限公司'),
        ('FUND', '嘉实基金管理有限公司'),
        ('WEALTH', '中信理财有限责任公司'),
        ('BROKER', '中信证券股份有限公司'),
        ('INSURANCE', '中国人寿保险股份有限公司'),
        ('BANK', '中国工商银行股份有限公司'),
        ('OTHER', '中央汇金资产管理有限责任公司')
    ]:
        company, created = FundCompany.objects.get_or_create(
            company_name=company_name,
            defaults={
                'company_type': company_type,
                'contact_info': f"{company_name}总部联系方式",
                'aum': Decimal(str(round(5000 + 1000 * len(fund_companies), 2)))
            }
        )
        fund_companies.append(company)
        if created:
            print(f"Created company: {company_name} ({company_type})")
        else:
            print(f"Company already exists: {company_name}")
    
    # Create funds
    funds = []
    for idx, (fund_name, manager_name) in enumerate([
        ('华夏债券A', '王丽丽'),
        ('博时信用债券A', '张三'),
        ('嘉实债券A', '李四'),
        ('华夏收益债券A', '王五'),
        ('博时宏观回报债券A', '赵六'),
    ]):
        # Spread the funds across the fund companies
        company = fund_companies[idx % 3]  # Use only the first 3 companies (FUND type)
        
        fund, created = Fund.objects.get_or_create(
            fund_name=fund_name,
            fund_company=company,
            defaults={
                'fund_manager': manager_name,
                'contact_email': f"{manager_name.lower()}@example.com",
                'contact_phone': f"010-8888-{1000+idx}"
            }
        )
        funds.append(fund)
        if created:
            print(f"Created fund: {fund_name} (Manager: {manager_name})")
        else:
            print(f"Fund already exists: {fund_name}")
    
    # Create persons (fund managers and company contacts)
    # For funds
    for idx, fund in enumerate(funds):
        # Primary fund manager
        person, created = Person.objects.get_or_create(
            fund=fund,
            name=fund.fund_manager,
            defaults={
                'role': '基金经理',
                'phone': f"010-8888-{2000+idx}",
                'mobile': f"139{10000000+idx}",
                'email': f"{fund.fund_manager.lower()}@example.com",
                'is_primary': True,
                'is_leader': False,
                'qq': f"{8000000+idx}",
                'wechat': f"wx_{fund.fund_manager}"
            }
        )
        if created:
            print(f"Created person: {person.name} (Role: {person.role})")
        else:
            print(f"Person already exists: {person.name}")
        
        # Add a trader
        trader_name = f"交易员{idx+1}"
        person, created = Person.objects.get_or_create(
            fund=fund,
            name=trader_name,
            defaults={
                'role': '交易员',
                'phone': f"010-8888-{3000+idx}",
                'mobile': f"138{10000000+idx}",
                'email': f"trader{idx+1}@example.com",
                'is_primary': False,
                'is_leader': False,
                'qq': f"{9000000+idx}",
                'wechat': f"wx_trader{idx+1}"
            }
        )
        if created:
            print(f"Created person: {person.name} (Role: {person.role})")
        else:
            print(f"Person already exists: {person.name}")
    
    # For companies
    for idx, company in enumerate(fund_companies[3:]):  # Skip fund companies
        # CEO
        ceo_name = f"{company.company_name[:2]}总裁"
        person, created = Person.objects.get_or_create(
            company=company,
            name=ceo_name,
            defaults={
                'role': '总裁',
                'phone': f"010-9999-{1000+idx}",
                'mobile': f"137{10000000+idx}",
                'email': f"ceo{idx+1}@example.com",
                'is_primary': True,
                'is_leader': True,
                'qq': f"{7000000+idx}",
                'wechat': f"wx_ceo{idx+1}"
            }
        )
        if created:
            print(f"Created person: {person.name} (Role: {person.role})")
        else:
            print(f"Person already exists: {person.name}")
        
        # Investment Manager
        manager_name = f"{company.company_name[:2]}投资总监"
        person, created = Person.objects.get_or_create(
            company=company,
            name=manager_name,
            defaults={
                'role': '投资总监',
                'phone': f"010-9999-{2000+idx}",
                'mobile': f"136{10000000+idx}",
                'email': f"im{idx+1}@example.com",
                'is_primary': False,
                'is_leader': True,
                'qq': f"{6000000+idx}",
                'wechat': f"wx_im{idx+1}"
            }
        )
        if created:
            print(f"Created person: {person.name} (Role: {person.role})")
        else:
            print(f"Person already exists: {person.name}")
        
        # Trader
        trader_name = f"{company.company_name[:2]}交易员"
        person, created = Person.objects.get_or_create(
            company=company,
            name=trader_name,
            defaults={
                'role': '交易员',
                'phone': f"010-9999-{3000+idx}",
                'mobile': f"135{10000000+idx}",
                'email': f"trader_co{idx+1}@example.com",
                'is_primary': False,
                'is_leader': False,
                'qq': f"{5000000+idx}",
                'wechat': f"wx_trader_co{idx+1}"
            }
        )
        if created:
            print(f"Created person: {person.name} (Role: {person.role})")
        else:
            print(f"Person already exists: {person.name}")
    
    # Create bond holdings
    # Funds holding bonds
    for idx, fund in enumerate(funds):
        # Each fund holds 2-3 bonds
        for bond_idx, bond_code in enumerate(list(bonds.keys())[idx:idx+3]):
            bond = bonds[bond_code]
            purchase_date = bond.issue_date + datetime.timedelta(days=30)
            
            # Some holdings are current, some are sold
            is_current = (idx + bond_idx) % 3 != 0
            sell_date = None if is_current else (purchase_date + datetime.timedelta(days=180))
            
            holding, created = BondHolding.objects.get_or_create(
                fund=fund,
                bond=bond,
                purchase_date=purchase_date,
                defaults={
                    'remaining_term_at_purchase': bond.remaining_term + Decimal('0.5'),
                    'holding_amount': Decimal(str(round(5000 + 1000 * idx, 2))),
                    'holding_percentage': Decimal(str(round(0.05 + 0.01 * idx, 4))),
                    'is_current_holding': is_current,
                    'sell_date': sell_date
                }
            )
            if created:
                print(f"Created fund holding: {fund.fund_name} - {bond.bond_code}")
            else:
                print(f"Fund holding already exists: {fund.fund_name} - {bond.bond_code}")
    
    # Companies holding bonds directly
    for idx, company in enumerate(fund_companies[3:]):  # Skip fund companies
        # Each company holds 1-2 bonds
        for bond_idx, bond_code in enumerate(list(bonds.keys())[idx*2:idx*2+2]):
            bond = bonds[bond_code]
            purchase_date = bond.issue_date + datetime.timedelta(days=45)
            
            # Some holdings are current, some are sold
            is_current = (idx + bond_idx) % 2 == 0
            sell_date = None if is_current else (purchase_date + datetime.timedelta(days=270))
            
            holding, created = BondHolding.objects.get_or_create(
                company=company,
                bond=bond,
                purchase_date=purchase_date,
                defaults={
                    'remaining_term_at_purchase': bond.remaining_term + Decimal('0.4'),
                    'holding_amount': Decimal(str(round(10000 + 2000 * idx, 2))),
                    'holding_percentage': Decimal(str(round(0.1 + 0.02 * idx, 4))),
                    'is_current_holding': is_current,
                    'sell_date': sell_date
                }
            )
            if created:
                print(f"Created company holding: {company.company_name} - {bond.bond_code}")
            else:
                print(f"Company holding already exists: {company.company_name} - {bond.bond_code}")
    
    print("Sample data creation complete!")

if __name__ == '__main__':
    create_sample_data() 