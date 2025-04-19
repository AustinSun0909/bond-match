from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import IntegrityError, transaction
from django.db.models import Q

from securities.models import Issuer, Bond, FundCompany, Fund, Person, BondHolding
from decimal import Decimal, InvalidOperation
import pandas as pd
import os
import datetime
import re

class Command(BaseCommand):
    help = 'Import bond data from Excel files'

    def add_arguments(self, parser):
        parser.add_argument('excel_file', type=str, help='Path to the Excel file')
        parser.add_argument('--sheet', type=str, help='Sheet name to import')
        parser.add_argument('--type', type=str, choices=['issuers', 'bonds', 'funds', 'holdings'], 
                            help='Type of data to import')

    def handle(self, *args, **options):
        file_path = options['excel_file']
        sheet_name = options.get('sheet')
        data_type = options.get('type', 'bonds')  # Default to bonds

        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f"File not found: {file_path}"))
            return

        try:
            # Read the Excel file
            if sheet_name:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
            else:
                df = pd.read_excel(file_path)

            # Call the appropriate import function based on data type
            if data_type == 'issuers':
                self.import_issuers(df)
            elif data_type == 'bonds':
                self.import_bonds(df)
            elif data_type == 'funds':
                self.import_funds(df)
            elif data_type == 'holdings':
                self.import_holdings(df)
            else:
                self.stdout.write(self.style.ERROR(f"Unknown data type: {data_type}"))
                return

            self.stdout.write(self.style.SUCCESS(f"Successfully imported {data_type} data from {file_path}"))
        
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error importing data: {str(e)}"))

    def import_issuers(self, df):
        """Import issuer data from the dataframe"""
        required_columns = ['issuer_name']
        self._validate_columns(df, required_columns)
        
        count = 0
        for _, row in df.iterrows():
            try:
                issuer_name = self._clean_text(row['issuer_name'])
                if not issuer_name:
                    continue
                    
                other_info = self._clean_text(row.get('other_info', ''))
                
                issuer, created = Issuer.objects.get_or_create(
                    issuer_name=issuer_name,
                    defaults={'other_info': other_info}
                )
                
                if created:
                    count += 1
                    self.stdout.write(f"Created issuer: {issuer.issuer_name}")
                else:
                    self.stdout.write(f"Issuer already exists: {issuer.issuer_name}")
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error creating issuer for row {row.name}: {str(e)}"))
                
        self.stdout.write(f"Created {count} new issuers")

    def import_bonds(self, df):
        """Import bond data from the dataframe"""
        required_columns = ['bond_code', 'issuer_name']
        self._validate_columns(df, required_columns)
        
        count = 0
        for _, row in df.iterrows():
            try:
                with transaction.atomic():
                    bond_code = self._clean_text(row['bond_code'])
                    issuer_name = self._clean_text(row['issuer_name'])
                    
                    if not bond_code or not issuer_name:
                        continue
                    
                    # Get or create the issuer
                    issuer, _ = Issuer.objects.get_or_create(
                        issuer_name=issuer_name,
                        defaults={'other_info': '从Excel导入'}
                    )
                    
                    # Extract issue date
                    issue_date = None
                    if 'issue_date' in row and pd.notna(row['issue_date']):
                        try:
                            issue_date = row['issue_date']
                            if isinstance(issue_date, str):
                                # Try to parse date from string with various formats
                                for fmt in ['%Y-%m-%d', '%Y/%m/%d', '%d-%m-%Y', '%d/%m/%Y']:
                                    try:
                                        issue_date = datetime.datetime.strptime(issue_date, fmt).date()
                                        break
                                    except ValueError:
                                        pass
                        except Exception:
                            issue_date = timezone.now().date()
                    else:
                        issue_date = timezone.now().date()
                    
                    # Extract term years
                    term_years = Decimal('0.00')
                    if 'term_years' in row and pd.notna(row['term_years']):
                        try:
                            term_years = Decimal(str(row['term_years']))
                        except (InvalidOperation, ValueError):
                            term_string = str(row['term_years'])
                            # Try to extract years from strings like "5Y", "3年", etc.
                            match = re.search(r'(\d+\.?\d*)', term_string)
                            if match:
                                try:
                                    term_years = Decimal(match.group(1))
                                except (InvalidOperation, ValueError):
                                    pass
                    
                    # Extract remaining term
                    remaining_term = Decimal('0.00')
                    if 'remaining_term' in row and pd.notna(row['remaining_term']):
                        try:
                            remaining_term = Decimal(str(row['remaining_term']))
                        except (InvalidOperation, ValueError):
                            pass
                            
                    # Extract bond name and other attributes
                    bond_name = self._clean_text(row.get('bond_name', '')) 
                    coupon_rate = self._clean_text(row.get('coupon_rate', ''))
                    bond_type = self._clean_text(row.get('bond_type', '公司债'))
                    
                    # Prepare other attributes
                    other_attributes = f"Name: {bond_name}"
                    if bond_type:
                        other_attributes += f", Bond type: {bond_type}"
                    if coupon_rate:
                        other_attributes += f", Coupon Rate: {coupon_rate}"
                    
                    # Create or update the bond
                    bond, created = Bond.objects.update_or_create(
                        bond_code=bond_code,
                        defaults={
                            'issuer': issuer,
                            'issue_date': issue_date,
                            'term_years': term_years,
                            'remaining_term': remaining_term,
                            'other_attributes': other_attributes,
                        }
                    )
                    
                    if created:
                        count += 1
                        self.stdout.write(f"Created bond: {bond.bond_code}")
                    else:
                        self.stdout.write(f"Updated bond: {bond.bond_code}")
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error processing bond for row {row.name}: {str(e)}"))
                
        self.stdout.write(f"Created {count} new bonds")

    def import_funds(self, df):
        """Import fund and fund company data from the dataframe"""
        required_columns = ['company_name', 'fund_name']
        self._validate_columns(df, required_columns)
        
        fund_count = 0
        company_count = 0
        person_count = 0
        
        for _, row in df.iterrows():
            try:
                with transaction.atomic():
                    company_name = self._clean_text(row['company_name'])
                    fund_name = self._clean_text(row['fund_name'])
                    
                    if not company_name or not fund_name:
                        continue
                    
                    # Get or create the fund company
                    company_type = self._clean_text(row.get('company_type', 'FUND'))
                    if company_type not in ['FUND', 'INSURANCE', 'BANK', 'OTHER']:
                        company_type = 'FUND'
                        
                    contact_info = self._clean_text(row.get('contact_info', ''))
                    aum = Decimal('0.00')
                    if 'aum' in row and pd.notna(row['aum']):
                        try:
                            aum = Decimal(str(row['aum']))
                        except (InvalidOperation, ValueError):
                            pass
                            
                    company, company_created = FundCompany.objects.get_or_create(
                        company_name=company_name,
                        defaults={
                            'company_type': company_type,
                            'contact_info': contact_info,
                            'aum': aum
                        }
                    )
                    
                    if company_created:
                        company_count += 1
                        self.stdout.write(f"Created fund company: {company.company_name}")
                    
                    # Get or create the fund
                    fund_manager = self._clean_text(row.get('fund_manager', 'Unknown'))
                    contact_email = self._clean_text(row.get('contact_email', 'unknown@example.com'))
                    contact_phone = self._clean_text(row.get('contact_phone', '000-0000-0000'))
                    
                    fund, fund_created = Fund.objects.get_or_create(
                        fund_company=company,
                        fund_name=fund_name,
                        defaults={
                            'fund_manager': fund_manager,
                            'contact_email': contact_email,
                            'contact_phone': contact_phone
                        }
                    )
                    
                    if fund_created:
                        fund_count += 1
                        self.stdout.write(f"Created fund: {fund.fund_name}")
                        
                        # Create persons associated with this fund
                        if fund_manager and fund_manager != 'Unknown':
                            try:
                                person, created = Person.objects.get_or_create(
                                    fund=fund,
                                    name=fund_manager,
                                    defaults={
                                        'role': '基金经理',
                                        'phone': contact_phone,
                                        'email': contact_email,
                                        'is_primary': True
                                    }
                                )
                                
                                if created:
                                    person_count += 1
                                    self.stdout.write(f"Created person: {person.name}")
                            except IntegrityError:
                                self.stdout.write(f"Person already exists for fund: {fund.fund_name}")
                        
                        # Look for additional persons in the data
                        traders = self._clean_text(row.get('traders', ''))
                        if traders:
                            for trader_info in traders.split(';'):
                                try:
                                    parts = trader_info.split(',')
                                    if len(parts) > 0:
                                        name = parts[0].strip()
                                        role = '交易员'
                                        phone = parts[1].strip() if len(parts) > 1 else ''
                                        email = parts[2].strip() if len(parts) > 2 else ''
                                        
                                        person, created = Person.objects.get_or_create(
                                            fund=fund,
                                            name=name,
                                            defaults={
                                                'role': role,
                                                'phone': phone,
                                                'email': email,
                                                'is_primary': False
                                            }
                                        )
                                        
                                        if created:
                                            person_count += 1
                                            self.stdout.write(f"Created person: {person.name}")
                                except Exception as e:
                                    self.stdout.write(self.style.WARNING(f"Error creating trader: {str(e)}"))
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error processing fund for row {row.name}: {str(e)}"))
                
        self.stdout.write(f"Created {company_count} new fund companies, {fund_count} new funds, and {person_count} new persons")

    def import_holdings(self, df):
        """Import bond holdings data from the dataframe"""
        required_columns = ['bond_code', 'fund_name', 'company_name']
        self._validate_columns(df, required_columns)
        
        count = 0
        for _, row in df.iterrows():
            try:
                with transaction.atomic():
                    bond_code = self._clean_text(row['bond_code'])
                    fund_name = self._clean_text(row['fund_name'])
                    company_name = self._clean_text(row['company_name'])
                    
                    if not bond_code or not fund_name or not company_name:
                        continue
                    
                    # Find the bond
                    try:
                        bond = Bond.objects.get(bond_code=bond_code)
                    except Bond.DoesNotExist:
                        self.stdout.write(self.style.WARNING(f"Bond not found: {bond_code}"))
                        continue
                    
                    # Find the fund
                    try:
                        fund = Fund.objects.get(
                            fund_name=fund_name,
                            fund_company__company_name=company_name
                        )
                    except Fund.DoesNotExist:
                        # Try to find a matching fund by name only
                        matching_funds = Fund.objects.filter(fund_name=fund_name)
                        if matching_funds.exists():
                            fund = matching_funds.first()
                            self.stdout.write(self.style.WARNING(
                                f"Fund company mismatch for '{fund_name}', using existing fund under company '{fund.fund_company.company_name}'"
                            ))
                        else:
                            self.stdout.write(self.style.WARNING(f"Fund not found: {fund_name} ({company_name})"))
                            continue
                    
                    # Parse purchase date
                    purchase_date = None
                    if 'purchase_date' in row and pd.notna(row['purchase_date']):
                        try:
                            purchase_date = row['purchase_date']
                            if isinstance(purchase_date, str):
                                # Try to parse date from string with various formats
                                for fmt in ['%Y-%m-%d', '%Y/%m/%d', '%d-%m-%Y', '%d/%m/%Y']:
                                    try:
                                        purchase_date = datetime.datetime.strptime(purchase_date, fmt).date()
                                        break
                                    except ValueError:
                                        pass
                        except Exception:
                            purchase_date = bond.issue_date + datetime.timedelta(days=30)
                    else:
                        purchase_date = bond.issue_date + datetime.timedelta(days=30)
                    
                    # Parse holding amount
                    holding_amount = Decimal('0.00')
                    if 'holding_amount' in row and pd.notna(row['holding_amount']):
                        try:
                            holding_amount = Decimal(str(row['holding_amount']))
                        except (InvalidOperation, ValueError):
                            pass
                    
                    # Parse holding percentage
                    holding_percentage = Decimal('0.00')
                    if 'holding_percentage' in row and pd.notna(row['holding_percentage']):
                        try:
                            holding_percentage = Decimal(str(row['holding_percentage']))
                        except (InvalidOperation, ValueError):
                            pass
                    
                    # Parse remaining term at purchase
                    remaining_term_at_purchase = Decimal('0.00')
                    if 'remaining_term_at_purchase' in row and pd.notna(row['remaining_term_at_purchase']):
                        try:
                            remaining_term_at_purchase = Decimal(str(row['remaining_term_at_purchase']))
                        except (InvalidOperation, ValueError):
                            remaining_term_at_purchase = bond.remaining_term
                    else:
                        remaining_term_at_purchase = bond.remaining_term
                    
                    # Determine if current holding
                    is_current_holding = True
                    if 'is_current_holding' in row and pd.notna(row['is_current_holding']):
                        is_current_string = str(row['is_current_holding']).lower()
                        if is_current_string in ('false', 'no', '0', 'n'):
                            is_current_holding = False
                    
                    # Create or update the holding
                    holding, created = BondHolding.objects.update_or_create(
                        fund=fund,
                        bond=bond,
                        purchase_date=purchase_date,
                        defaults={
                            'remaining_term_at_purchase': remaining_term_at_purchase,
                            'holding_amount': holding_amount,
                            'holding_percentage': holding_percentage,
                            'is_current_holding': is_current_holding
                        }
                    )
                    
                    if created:
                        count += 1
                        self.stdout.write(f"Created bond holding: {fund.fund_name} - {bond.bond_code}")
                    else:
                        self.stdout.write(f"Updated bond holding: {fund.fund_name} - {bond.bond_code}")
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error processing holding for row {row.name}: {str(e)}"))
                
        self.stdout.write(f"Created {count} new bond holdings")

    def _validate_columns(self, df, required_columns):
        """Check if dataframe has required columns"""
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")

    def _clean_text(self, text):
        """Clean and normalize text fields"""
        if pd.isna(text):
            return ''
        return str(text).strip() 