# -*- coding: utf-8 -*-
"""
EMBER · rebuild the whole catalog from catalog/ember_catalog_data.py
Deletes existing products / categories / brands, then creates the new Amazon-style
taxonomy, brands, products (with variants, images if files exist, specs in description)
and approved demo reviews.
Run:  python manage.py rebuild_catalog
"""
import os
import random
from datetime import timedelta
from decimal import Decimal

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from accounts.models import User
from catalog.models import Brand, Category, Product, ProductImage, ProductVariant
from reviews.models import Review
from catalog.ember_catalog_data import CATEGORIES, BRANDS, PRODUCTS, VARIANTS, REVIEWS


class Command(BaseCommand):
    help = "EMBER: rebuild catalog (destructive: removes existing products, categories, brands)."

    def handle(self, *args, **options):
        out = self.stdout.write
        with transaction.atomic():
            old_pc = Product.objects.count()
            Product.objects.all().delete()
            Category.objects.all().delete()
            Brand.objects.all().delete()
            out('Removed %d old products.' % old_pc)

            # ---- categories (recursive) ----
            cat_map = {}
            order_n = [0]

            def create_tree(nodes, parent=None):
                for node in nodes:
                    order_n[0] += 1
                    cat = Category.objects.create(
                        name=node['name'], slug=node['slug'], parent=parent,
                        is_active=True, order=order_n[0],
                    )
                    cat_map[node['slug']] = cat
                    if node.get('children'):
                        create_tree(node['children'], cat)

            create_tree(CATEGORIES)
            out('Created %d categories.' % Category.objects.count())

            # ---- brands ----
            brands = {}
            for name, slug in BRANDS:
                brands[slug] = Brand.objects.create(name=name, slug=slug, is_active=True)
            out('Created %d brands.' % Brand.objects.count())

            # ---- products ----
            now = timezone.now()
            img_total = 0
            for idx, item in enumerate(PRODUCTS, start=1):
                cat = cat_map.get(item['category'])
                if cat is None:
                    out('!! missing category %s for %s (skipped)' % (item['category'], item['slug']))
                    continue
                brand = brands.get(item['brand']) if item.get('brand') else None

                desc = item.get('desc', '')
                if item.get('specs'):
                    desc += '\n\nمشخصات فنی:\n' + '\n'.join('• %s: %s' % (k, v) for k, v in item['specs'])

                stock = int(item.get('stock', 0))
                p = Product.objects.create(
                    name=item['name'],
                    slug=item['slug'],
                    sku='EMB-%04d' % idx,
                    category=cat,
                    brand=brand,
                    short_description=item.get('short', '')[:500],
                    description=desc,
                    base_price=Decimal(item['price']),
                    sale_price=Decimal(item['sale']) if item.get('sale') else None,
                    stock=stock,
                    is_available=stock > 0,
                    is_active=True,
                    is_featured=bool(item.get('featured')),
                    is_bestseller=bool(item.get('bestseller')),
                    is_new_arrival=bool(item.get('is_new', False)) or int(item.get('days_old', 30)) <= 7,
                )
                updates = {'discount_percent': p.calculate_discount_percent()}
                updates['created_at'] = now - timedelta(days=int(item.get('days_old', 30)))
                Product.objects.filter(pk=p.pk).update(**updates)

                # images (generated separately; attach if the files already exist)
                for n in range(1, int(item.get('img_count', 1)) + 1):
                    rel = 'products/%s-%d.jpg' % (item['slug'], n)
                    if os.path.exists(os.path.join(settings.MEDIA_ROOT, rel)):
                        ProductImage.objects.create(product=p, image=rel, is_feature=(n == 1), order=n)
                        img_total += 1

                # variants
                for (vname, vsku, vprice, vstock) in VARIANTS.get(item['slug'], []):
                    ProductVariant.objects.create(
                        product=p, name=vname, sku=vsku,
                        price_override=Decimal(vprice), stock=vstock, is_active=True,
                    )

            out('Created %d products with %d images.' % (Product.objects.count(), img_total))

            # ---- reviews ----
            rnd = random.Random(7)
            reviewer_cache = {}
            r_count = 0

            def get_reviewer(full_name):
                if full_name in reviewer_cache:
                    return reviewer_cache[full_name]
                parts = full_name.split()
                email = 'fan%03d@shop.local' % (len(reviewer_cache) + 1)
                u = User.objects.create_user(
                    email=email, password=None,
                    first_name=parts[0], last_name=parts[1] if len(parts) > 1 else '',
                )
                reviewer_cache[full_name] = u
                return u

            for slug, revs in REVIEWS.items():
                product = Product.objects.filter(slug=slug).first()
                if product is None:
                    continue
                for (author, title, text, rating) in revs:
                    u = get_reviewer(author)
                    r = Review.objects.create(
                        product=product, user=u, rating=rating, title=title,
                        comment=text, is_approved=True, is_verified_buyer=True,
                    )
                    Review.objects.filter(pk=r.pk).update(
                        created_at=now - timedelta(days=rnd.randint(1, 60)),
                    )
                    r_count += 1
            out('Created %d reviews from %d reviewers.' % (r_count, len(reviewer_cache)))
            out('rebuild_catalog: DONE')
