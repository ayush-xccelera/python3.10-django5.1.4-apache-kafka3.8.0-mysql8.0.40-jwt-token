from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from products.models import Product

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed the database with demo users and products (idempotent).'

    def handle(self, *args, **options):
        user, created = User.objects.get_or_create(
            username='demo',
            defaults={'email': 'demo@example.com'},
        )
        if created:
            user.set_password('DemoPass123!')
            user.save()
            self.stdout.write(self.style.SUCCESS('Created demo user (demo / DemoPass123!)'))
        else:
            self.stdout.write('Demo user already exists.')

        products = [
            {'name': 'Wireless Mouse', 'description': 'Ergonomic wireless mouse', 'price': '19.99', 'stock_quantity': 100},
            {'name': 'Mechanical Keyboard', 'description': 'RGB mechanical keyboard', 'price': '59.99', 'stock_quantity': 50},
            {'name': 'USB-C Hub', 'description': '7-in-1 USB-C hub', 'price': '29.99', 'stock_quantity': 75},
            {'name': '27" Monitor', 'description': '4K IPS monitor', 'price': '299.99', 'stock_quantity': 20},
            {'name': 'Webcam', 'description': '1080p HD webcam', 'price': '39.99', 'stock_quantity': 0},
        ]

        for p in products:
            obj, created = Product.objects.get_or_create(
                name=p['name'],
                defaults={
                    'description': p['description'],
                    'price': p['price'],
                    'stock_quantity': p['stock_quantity'],
                    'owner': user,
                },
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created product: {obj.name}'))
            else:
                self.stdout.write(f'Product already exists: {obj.name}')

        self.stdout.write(self.style.SUCCESS('Seeding complete.'))
