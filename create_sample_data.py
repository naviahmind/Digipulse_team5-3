#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from Webtintuc.models import Category, Author, News
from django.utils import timezone

# Clear existing data
News.objects.all().delete()
Author.objects.all().delete()
Category.objects.all().delete()

# Create categories
cat1 = Category.objects.create(name='Technology', slug='technology')
cat2 = Category.objects.create(name='Sports', slug='sports')
cat3 = Category.objects.create(name='Entertainment', slug='entertainment')

# Create authors
auth1 = Author.objects.create(name='John Doe', email='john@example.com')
auth2 = Author.objects.create(name='Jane Smith', email='jane@example.com')

# Create news
news1 = News.objects.create(
    title='Breaking: New Python Release',
    slug='breaking-new-python-release',
    category=cat1,
    author=auth1,
    description='Latest Python version released with new features.',
    content='Python 3.14 is now available with improved performance and security features.',
    is_featured=True,
    status='published',
    views=100,
    created_at=timezone.now(),
    published_at=timezone.now()
)

news2 = News.objects.create(
    title='AI Breakthrough in Machine Learning',
    slug='ai-breakthrough-ml',
    category=cat1,
    author=auth2,
    description='Researchers announce major AI advancement.',
    content='A new deep learning model outperforms previous benchmarks by 40%.',
    is_featured=True,
    status='published',
    views=250,
    created_at=timezone.now(),
    published_at=timezone.now()
)

news3 = News.objects.create(
    title='Team Wins Championship',
    slug='team-wins-championship',
    category=cat2,
    author=auth1,
    description='Local team becomes champions.',
    content='The team defeated rivals in a thrilling final match.',
    is_featured=False,
    status='published',
    views=180,
    created_at=timezone.now(),
    published_at=timezone.now()
)

news4 = News.objects.create(
    title='Movie Release This Weekend',
    slug='movie-release-weekend',
    category=cat3,
    author=auth2,
    description='Blockbuster film hits theaters.',
    content='The highly anticipated movie arrives in theaters this Friday.',
    is_featured=True,
    status='published',
    views=320,
    created_at=timezone.now(),
    published_at=timezone.now()
)

news5 = News.objects.create(
    title='Concert Announcement',
    slug='concert-announcement',
    category=cat3,
    author=auth1,
    description='Popular band announces tour dates.',
    content='The band will perform in multiple cities starting next month.',
    is_featured=False,
    status='published',
    views=95,
    created_at=timezone.now(),
    published_at=timezone.now()
)

print("Sample data created successfully!")
print(f"Created {Category.objects.count()} categories")
print(f"Created {Author.objects.count()} authors")
print(f"Created {News.objects.count()} news articles")
