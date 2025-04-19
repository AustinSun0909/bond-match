import random
from datetime import date, timedelta
from decimal import Decimal
from django.core.management.base import BaseCommand
from securities.models import Issuer, Bond

class Command(BaseCommand):
    help = 'Seeds the database with sample bonds'

    def handle(self, *args, **options):
        # Create issuers
        issuers = []
        
        issuer_names = [
            "中国银行", "工商银行", "建设银行", "农业银行", "招商银行",
            "交通银行", "浦发银行", "兴业银行", "平安银行", "华夏银行",
            "中国石油", "中国石化", "中国移动", "中国电信", "中国联通",
            "中国铁建", "中国建筑", "中国中铁", "上海电力", "国家电网"
        ]
        
        for name in issuer_names:
            issuer, created = Issuer.objects.get_or_create(
                issuer_name=name,
                defaults={
                    'other_info': f'Sample issuer data for {name}'
                }
            )
            issuers.append(issuer)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created issuer: {name}'))
            else:
                self.stdout.write(f'Issuer already exists: {name}')
        
        # Create bonds
        bond_types = ['国债', '企业债', '金融债', '地方债', '次级债', '公司债']
        prefix_codes = ['10', '11', '12', '13', '14', '15']
        
        # Today's date
        today = date.today()
        
        # Create 100 bonds
        for i in range(100):
            issuer = random.choice(issuers)
            bond_type = random.choice(bond_types)
            prefix = random.choice(prefix_codes)
            
            # Generate a random code
            bond_code = f'{prefix}{random.randint(1000000, 9999999)}'
            
            # Generate a random name
            bond_name = f'{issuer.issuer_name}{random.randint(1, 20)}期{bond_type}'
            
            # Random issue date in the past 5 years
            issue_date = today - timedelta(days=random.randint(1, 1825))
            
            # Random term in years (1-10 years)
            term_years = Decimal(str(round(random.uniform(1.0, 10.0), 2)))
            
            # Calculate remaining term
            days_since_issue = (today - issue_date).days
            total_days = term_years * 365
            remaining_days = max(0, total_days - days_since_issue)
            remaining_term = Decimal(str(round(remaining_days / 365, 2)))
            
            # Can be redeemed?
            can_be_redeemed = random.choice([True, False])
            
            bond, created = Bond.objects.get_or_create(
                bond_code=bond_code,
                defaults={
                    'issuer': issuer,
                    'issue_date': issue_date,
                    'term_years': term_years,
                    'remaining_term': remaining_term,
                    'can_be_redeemed': can_be_redeemed,
                    'other_attributes': f'Bond type: {bond_type}, Name: {bond_name}'
                }
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created bond: {bond_name} ({bond_code})'))
            else:
                self.stdout.write(f'Bond already exists: {bond_code}')
        
        self.stdout.write(self.style.SUCCESS('Successfully seeded the database with sample bonds')) 