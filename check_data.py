import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from Webtintuc.models import Category, Author, News

print("📊 Thống kê Database:")
print(f"- Categories: {Category.objects.count()}")
print(f"- Authors: {Author.objects.count()}")
print(f"- News: {News.objects.count()}")
print(f"- News published: {News.objects.filter(status='published').count()}")
print(f"- News featured: {News.objects.filter(is_featured=True).count()}")

print("\n📝 Danh sách tin tức:")
for news in News.objects.all():
    print(f"  - {news.title} (status={news.status}, featured={news.is_featured})")
