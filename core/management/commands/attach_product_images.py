# -*- coding: utf-8 -*-
"""
EMBER · attach generated media/products/<slug>-N.jpg files to products
(idempotent; safe to re-run after the image generator finishes).
Run:  python manage.py attach_product_images
"""
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from catalog.models import Product, ProductImage


class Command(BaseCommand):
    help = "Attach generated product images (media/products/<slug>-N.jpg) to products."

    def handle(self, *args, **options):
        added = 0
        fixed_feature = 0
        for p in Product.objects.all():
            for n in range(1, 4):
                rel = 'products/%s-%d.jpg' % (p.slug, n)
                if not os.path.exists(os.path.join(settings.MEDIA_ROOT, rel)):
                    continue
                if p.images.filter(image=rel).exists():
                    continue
                has_feature = p.images.filter(is_feature=True).exists()
                ProductImage.objects.create(
                    product=p, image=rel,
                    is_feature=(n == 1 and not has_feature),
                    order=n,
                )
                added += 1
            if p.images.exists() and not p.images.filter(is_feature=True).exists():
                first = p.images.order_by('order', 'id').first()
                first.is_feature = True
                first.save(update_fields=['is_feature'])
                fixed_feature += 1
        self.stdout.write('attach_product_images: added %d, feature-fixed %d.' % (added, fixed_feature))
