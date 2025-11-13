from django.core.management.base import BaseCommand
from expenses.models import Category


class Command(BaseCommand):
    help = 'Create default expense categories for SplitEase'

    def handle(self, *args, **options):
        categories_data = [
            # Food & Dining
            ('Food & Dining', 'Restaurant, groceries, and meals'),
            ('Groceries', 'Grocery shopping and food items'),
            ('Restaurants', 'Eating out at restaurants and cafes'),
            ('Delivery', 'Food delivery services'),
            
            # Travel & Transport
            ('Travel', 'Travel expenses including flights and hotels'),
            ('Transport', 'Local transportation costs'),
            ('Fuel', 'Gas and fuel expenses'),
            ('Taxi/Uber', 'Ride-sharing services'),
            ('Bus/Train', 'Public transportation tickets'),
            ('Parking', 'Parking fees and charges'),
            ('Hotels', 'Accommodation during travel'),
            ('Flights', 'Airline tickets'),
            
            # Entertainment & Activities
            ('Entertainment', 'Movies, shows, and entertainment'),
            ('Party/Events', 'Parties, concerts, and events'),
            ('Movies', 'Movie tickets and cinema'),
            ('Games', 'Video games and gaming'),
            ('Sports', 'Sports activities and memberships'),
            ('Concerts', 'Concert and live show tickets'),
            
            # Shopping
            ('Shopping', 'General shopping and retail'),
            ('Clothing', 'Clothes and fashion items'),
            ('Electronics', 'Electronics and gadgets'),
            ('Books', 'Books and reading materials'),
            ('Home Goods', 'Household items and furnishings'),
            
            # Utilities & Bills
            ('Utilities', 'Electric, water, and gas bills'),
            ('Internet', 'Internet and phone bills'),
            ('Rent', 'Rent payments'),
            ('Insurance', 'Insurance premiums'),
            
            # Health & Personal Care
            ('Health', 'Medical and health expenses'),
            ('Medications', 'Medicines and prescriptions'),
            ('Gym', 'Gym membership and fitness'),
            ('Personal Care', 'Haircuts, salon, and personal hygiene'),
            
            # Other
            ('Other', 'Miscellaneous expenses'),
            ('Gifts', 'Gifts and presents'),
            ('Subscriptions', 'Monthly subscriptions and memberships'),
        ]
        
        created_count = 0
        for name, description in categories_data:
            category, created = Category.objects.get_or_create(
                name=name,
                defaults={'description': description}
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created category: {name}')
                )
            else:
                self.stdout.write(f'Category already exists: {name}')
        
        self.stdout.write(
            self.style.SUCCESS(f'\n✓ Total new categories created: {created_count}')
        )
