from django.urls import path
from . import views

app_name = 'webtintuc'

urlpatterns = [
    path('', views.index, name='index'),
    path('moi-nhat/', views.latest_news, name='latest_news'),
    path('tin-nong/', views.trending_news, name='trending_news'),
    path('xem-nhieu/', views.most_viewed, name='most_viewed'),
    path('tin/<slug:slug>/', views.post_detail, name='post_detail'),
    path('tim-kiem/', views.search_posts, name='search'),
    path('danh-muc/<slug:slug>/', views.category_posts, name='category'),
    path('category/<slug:slug>/posts/', views.category_news, name='category_news'),

    # Reaction
    path('tin/<slug:slug>/react/', views.react_post, name='react_post'),

    # Comments
    path('binh-luan/<int:comment_id>/sua/', views.edit_comment, name='edit_comment'),
    path('binh-luan/<int:comment_id>/xoa/', views.delete_comment, name='delete_comment'),

    # Follow category
    path('danh-muc/<slug:slug>/follow/', views.follow_category, name='follow_category'),

    # Notifications
    path('thong-bao/', views.notifications, name='notifications'),
    path('api/thong-bao/', views.notifications_api, name='notifications_api'),

    # Profile
    path('nguoi-dung/<str:username>/', views.user_profile, name='user_profile'),
    path('chinh-sua-profile/', views.edit_profile, name='edit_profile'),

    # Admin: posts
    path('tao-bai-viet/', views.create_post, name='create_post'),
    path('chinh-sua/<slug:slug>/', views.edit_post, name='edit_post'),
    path('xoa-bai-viet/<slug:slug>/', views.delete_post, name='delete_post'),
    path('bai-viet-cua-toi/', views.my_posts, name='my_posts'),
    path('them-danh-muc/', views.add_category_ajax, name='add_category_ajax'),
    path('them-tag/', views.add_tag_ajax, name='add_tag_ajax'),

    # Admin: user management
    path('quan-ly-nguoi-dung/', views.manage_users, name='manage_users'),
    path('quan-ly-nguoi-dung/<int:user_id>/khoa/', views.toggle_user_active, name='toggle_user_active'),
    path('quan-ly-nguoi-dung/<int:user_id>/quan-tri-vien/', views.toggle_user_admin, name='toggle_user_admin'),
    path('quan-ly-nguoi-dung/<int:user_id>/phan-quyen/', views.set_user_role, name='set_user_role'),
    path('quan-ly-nguoi-dung/<int:user_id>/xoa/', views.delete_user, name='delete_user'),
    path('quan-ly-nguoi-dung/<int:user_id>/doi-mat-khau/', views.reset_user_password, name='reset_user_password'),

    # Admin: advertisement management
    path('quan-ly-quang-cao/', views.manage_ads, name='manage_ads'),
    path('quan-ly-quang-cao/them/', views.create_ad, name='create_ad'),
    path('quan-ly-quang-cao/<int:ad_id>/sua/', views.edit_ad, name='edit_ad'),
    path('quan-ly-quang-cao/<int:ad_id>/xoa/', views.delete_ad, name='delete_ad'),
    path('quan-ly-quang-cao/<int:ad_id>/bat-tat/', views.toggle_ad, name='toggle_ad'),

    # Auth
    path('dang-ky/', views.register_view, name='register'),
    path('dang-nhap/', views.login_view, name='login'),
    path('dang-xuat/', views.logout_view, name='logout'),
    path('chinh-sach/', views.chinh_sach, name='chinh_sach'),
    path('quang-cao/', views.quang_cao, name='quang_cao'),
    path('huong-dan/', views.huong_dan, name='huong_dan'),
    path('faq/', views.faq, name='faq'),
]
