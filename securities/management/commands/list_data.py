from django.core.management.base import BaseCommand
from securities.models import Issuer, Bond, Fund, FundCompany, BondHolding, Person
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Lists imported data for verification'

    def add_arguments(self, parser):
        parser.add_argument(
            '--model',
            type=str,
            help='Model name to list (issuer, bond, fund, company, holding, person)',
        )
        
        parser.add_argument(
            '--id',
            type=int,
            help='ID to filter by',
        )
        
        parser.add_argument(
            '--search',
            type=str,
            help='Search term',
        )
        
        parser.add_argument(
            '--limit',
            type=int,
            default=10,
            help='Limit results (default: 10)',
        )

    def handle(self, *args, **options):
        model_name = (options.get('model', '') or '').lower()
        obj_id = options.get('id')
        search = options.get('search')
        limit = options.get('limit', 10)
        
        model_map = {
            'issuer': Issuer,
            'bond': Bond,
            'fund': Fund,
            'company': FundCompany,
            'holding': BondHolding,
            'person': Person,
            'user': User,
        }
        
        if not model_name:
            # Show summary of all models
            self.stdout.write("== Data Summary ==")
            self.stdout.write(f"Issuers: {Issuer.objects.count()}")
            self.stdout.write(f"Bonds: {Bond.objects.count()}")
            self.stdout.write(f"Fund Companies: {FundCompany.objects.count()}")
            self.stdout.write(f"Funds: {Fund.objects.count()}")
            self.stdout.write(f"Bond Holdings: {BondHolding.objects.count()}")
            self.stdout.write(f"Persons: {Person.objects.count()}")
            self.stdout.write(f"Users: {User.objects.count()}")
            self.stdout.write("\nUse --model to see specific data (e.g. --model=bond)")
            return
        
        if model_name not in model_map:
            self.stdout.write(self.style.ERROR(f"Unknown model: {model_name}"))
            self.stdout.write("Available models: " + ", ".join(model_map.keys()))
            return
        
        model = model_map[model_name]
        queryset = model.objects.all()
        
        if obj_id:
            queryset = queryset.filter(id=obj_id)
        
        if search:
            # Search by common fields for each model
            if model_name == 'issuer':
                queryset = queryset.filter(issuer_name__icontains=search)
            elif model_name == 'bond':
                queryset = queryset.filter(bond_code__icontains=search)
            elif model_name == 'fund':
                queryset = queryset.filter(fund_name__icontains=search)
            elif model_name == 'company':
                queryset = queryset.filter(company_name__icontains=search)
            elif model_name == 'person':
                queryset = queryset.filter(name__icontains=search)
            elif model_name == 'user':
                queryset = queryset.filter(username__icontains=search)
        
        queryset = queryset[:limit]
        
        if not queryset.exists():
            self.stdout.write(f"No {model_name} records found")
            return
        
        # Display results based on model type
        self.stdout.write(f"== {model_name.title()} Data ({queryset.count()} results) ==")
        
        for i, obj in enumerate(queryset, 1):
            self.stdout.write(f"\n{i}. {obj} (ID: {obj.id})")
            
            if model_name == 'issuer':
                self.stdout.write(f"   Other Info: {obj.other_info}")
                self.stdout.write(f"   Bond Count: {obj.bonds.count()}")
            
            elif model_name == 'bond':
                self.stdout.write(f"   Issuer: {obj.issuer.issuer_name}")
                self.stdout.write(f"   Term: {obj.term_years} years")
                self.stdout.write(f"   Issue Date: {obj.issue_date}")
                if obj.other_attributes:
                    self.stdout.write(f"   Other Attributes: {obj.other_attributes}")
            
            elif model_name == 'fund':
                self.stdout.write(f"   Company: {obj.fund_company.company_name}")
                self.stdout.write(f"   Manager: {obj.fund_manager}")
                self.stdout.write(f"   Holdings Count: {obj.bond_holdings.count()}")
                
            elif model_name == 'company':
                self.stdout.write(f"   Type: {obj.get_company_type_display()}")
                self.stdout.write(f"   AUM: {obj.aum:,}")
                self.stdout.write(f"   Fund Count: {obj.funds.count()}")
                
            elif model_name == 'holding':
                self.stdout.write(f"   Fund: {obj.fund.fund_name}")
                self.stdout.write(f"   Bond: {obj.bond.bond_code}")
                self.stdout.write(f"   Amount: {obj.holding_amount:,}")
                self.stdout.write(f"   Percentage: {obj.holding_percentage}%")
                
            elif model_name == 'person':
                self.stdout.write(f"   Fund: {obj.fund.fund_name}")
                self.stdout.write(f"   Role: {obj.role}")
                self.stdout.write(f"   Primary: {'Yes' if obj.is_primary else 'No'}")
                if obj.phone:
                    self.stdout.write(f"   Phone: {obj.phone}")
                if obj.email:
                    self.stdout.write(f"   Email: {obj.email}")
                
            elif model_name == 'user':
                self.stdout.write(f"   Email: {obj.email}")
                self.stdout.write(f"   Staff: {'Yes' if obj.is_staff else 'No'}")
                self.stdout.write(f"   Superuser: {'Yes' if obj.is_superuser else 'No'}")
        
        self.stdout.write(self.style.SUCCESS(f"\nSuccessfully listed {queryset.count()} {model_name} records")) 