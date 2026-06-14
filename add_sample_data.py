import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from Webtintuc.models import Category, Author, News
from django.utils import timezone

# Xóa dữ liệu cũ
Category.objects.all().delete()
Author.objects.all().delete()
News.objects.all().delete()

# 1. Tạo Categories
categories = [
    {"name": "Công Nghệ", "slug": "cong-nghe", "description": "Tin tức công nghệ", "icon": "fa-laptop", "color": "#667eea"},
    {"name": "AI", "slug": "ai", "description": "Tin tức AI", "icon": "fa-robot", "color": "#764ba2"},
    {"name": "Fintech", "slug": "fintech", "description": "Tin tức Fintech", "icon": "fa-credit-card", "color": "#00d4ff"},
    {"name": "Chứng Khoán", "slug": "chung-khoan", "description": "Tin tức chứng khoán", "icon": "fa-chart-line", "color": "#ffa500"},
    {"name": "Startups", "slug": "startups", "description": "Tin tức startup", "icon": "fa-rocket", "color": "#ff6b6b"},
]

cat_objs = {}
for cat in categories:
    obj = Category.objects.create(**cat)
    cat_objs[cat['slug']] = obj

print(f"✅ Đã tạo {len(cat_objs)} danh mục")

# 2. Tạo Authors
authors = [
    {"name": "Nguyễn Bảo", "email": "nguyenbao@tintuc.com", "bio": "Nhà báo công nghệ"},
    {"name": "Lê Minh", "email": "leminh@tintuc.com", "bio": "Chuyên gia AI"},
    {"name": "Đỗ Anh", "email": "doanh@tintuc.com", "bio": "Biên tập viên cao cấp"},
]

author_objs = []
for author in authors:
    obj = Author.objects.create(**author)
    author_objs.append(obj)

print(f"✅ Đã tạo {len(author_objs)} tác giả")

# 3. Tạo News
news_list = [
    {
        "title": "Công ty startup Việt vừa nhận vốn đầu tư 100 triệu USD",
        "slug": "startup-vietnam-100m",
        "category": cat_objs['startups'],
        "author": author_objs[0],
        "description": "Một công ty startup công nghệ Việt Nam vừa hoàn thành vòn gọi vốn Series B với số tiền lên tới 100 triệu USD",
        "content": "<p>Một công ty startup công nghệ Việt Nam vừa hoàn thành vòng gọi vốn Series B với số tiền lên tới 100 triệu USD. Đây là một bước tiến lớn trong sự phát triển của ngành công nghệ tại Việt Nam.</p><h2>Những Điểm Nổi Bật</h2><p>Vòng gọi vốn này được dẫn dắt bởi các quỹ đầu tư hàng đầu từ Silicon Valley. Công ty sẽ sử dụng số tiền này để mở rộng quy mô, phát triển sản phẩm mới và tuyển dụng nhân tài.</p>",
        "is_featured": True,
        "status": "published"
    },
    {
        "title": "OpenAI phát hành GPT-5 với khả năng xử lý dữ liệu siêu mạnh",
        "slug": "openai-gpt5",
        "category": cat_objs['ai'],
        "author": author_objs[1],
        "description": "OpenAI vừa công bố phiên bản mới nhất của mô hình ngôn ngữ GPT-5 với những cải thiện đáng kể",
        "content": "<p>OpenAI vừa công bố phiên bản mới nhất của mô hình ngôn ngữ GPT-5 với những cải thiện đáng kể về hiệu suất và khả năng xử lý. Mô hình này có thể xử lý khối lượng dữ liệu lớn hơn.</p>",
        "is_featured": False,
        "status": "published"
    },
    {
        "title": "Apple ra mắt iPhone 16 Pro Max với chip A19 Pro",
        "slug": "apple-iphone16",
        "category": cat_objs['cong-nghe'],
        "author": author_objs[2],
        "description": "Apple đã chính thức giới thiệu dòng iPhone 16 Pro Max mới với bộ xử lý A19 Pro mạnh mẽ",
        "content": "<p>Apple đã chính thức giới thiệu dòng iPhone 16 Pro Max mới với bộ xử lý A19 Pro mạnh mẽ. Thiết bị này hỗ trợ 5G nhanh hơn và pin được cải thiện đáng kể.</p>",
        "is_featured": False,
        "status": "published"
    },
    {
        "title": "Meta Platforms tăng đầu tư vào công nghệ Metaverse",
        "slug": "meta-metaverse",
        "category": cat_objs['cong-nghe'],
        "author": author_objs[0],
        "description": "Meta Platforms vừa công bố kế hoạch tăng đầu tư hàng tỷ đô la vào phát triển Metaverse",
        "content": "<p>Meta Platforms vừa công bố kế hoạch tăng đầu tư hàng tỷ đô la vào phát triển Metaverse. Công ty tin rằng đây sẽ là tương lai của internet.</p>",
        "is_featured": False,
        "status": "published"
    },
    {
        "title": "Google Gemini 2.0 có khả năng hiểu hình ảnh tốt hơn",
        "slug": "google-gemini2",
        "category": cat_objs['ai'],
        "author": author_objs[1],
        "description": "Google vừa phát hành Gemini 2.0 với khả năng xử lý hình ảnh được cải thiện đáng kể",
        "content": "<p>Google vừa phát hành Gemini 2.0 với khả năng xử lý hình ảnh được cải thiện đáng kể. AI này giờ có thể phân tích các hình ảnh phức tạp với độ chính xác cao.</p>",
        "is_featured": False,
        "status": "published"
    },
    {
        "title": "Nvidia đạt giá trị vốn hóa thị trường 3 nghìn tỷ USD",
        "slug": "nvidia-stock",
        "category": cat_objs['chung-khoan'],
        "author": author_objs[2],
        "description": "Nvidia trở thành công ty thứ ba đạt giá trị vốn hóa thị trường 3 nghìn tỷ USD",
        "content": "<p>Nvidia trở thành công ty thứ ba đạt giá trị vốn hóa thị trường 3 nghìn tỷ USD. Sự tăng trưởng này được thúc đẩy bởi nhu cầu cao về chip AI.</p>",
        "is_featured": False,
        "status": "published"
    },
    {
        "title": "Bitcoin vượt mức 100,000 USD lần đầu tiên",
        "slug": "bitcoin-100k",
        "category": cat_objs['fintech'],
        "author": author_objs[0],
        "description": "Bitcoin vừa phá vỡ mốc 100,000 USD lần đầu tiên trong lịch sử",
        "content": "<p>Bitcoin vừa phá vỡ mốc 100,000 USD lần đầu tiên trong lịch sử. Đây được coi là một cột mốc quan trọng cho thị trường tiền điện tử.</p>",
        "is_featured": False,
        "status": "published"
    },
    {
        "title": "Thương mại điện tử Việt Nam tăng trưởng 30% năm 2024",
        "slug": "ecommerce-vietnam",
        "category": cat_objs['fintech'],
        "author": author_objs[2],
        "description": "Lĩnh vực thương mại điện tử Việt Nam ghi nhận tốc độ tăng trưởng ấn tượng 30%",
        "content": "<p>Lĩnh vực thương mại điện tử Việt Nam ghi nhận tốc độ tăng trưởng ấn tượng 30% so với năm trước. Xu hướng mua sắm online tiếp tục tăng mạnh.</p>",
        "is_featured": False,
        "status": "published"
    },
]

for news_data in news_list:
    news = News.objects.create(**news_data)
    news.views = 100 + news.id * 50
    news.save()

print(f"✅ Đã tạo {len(news_list)} bài viết")
print("\n✨ Dữ liệu sample đã được thêm vào database thành công!")
