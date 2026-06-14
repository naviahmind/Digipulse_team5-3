from django.contrib import admin
from .models import Category, Post, Tag, Comment, Advertisement


# ==================== CATEGORY ADMIN ====================
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'category_type', 'created_at')
    list_filter = ('category_type', 'created_at')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


# ==================== TAG ADMIN ====================
@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


# ==================== POST ADMIN ====================
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'status', 'post_type', 'views_count', 'created_at')
    list_filter = ('status', 'post_type', 'category', 'created_at')
    search_fields = ('title', 'slug', 'content')
    filter_horizontal = ('tags',)
    prepopulated_fields = {'slug': ('title',)}
    fieldsets = (
        ('Thông tin cơ bản', {
            'fields': ('title', 'slug', 'post_type', 'category')
        }),
        ('Nội dung', {
            'fields': ('summary', 'content', 'thumbnail')
        }),
        ('Tác giả & Thẻ', {
            'fields': ('author', 'tags')
        }),
        ('Đăng bài', {
            'fields': ('status', 'views_count', 'created_at', 'published_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at', 'views_count')


# ==================== COMMENT ADMIN ====================
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'is_approved', 'created_at')
    list_filter = ('is_approved', 'created_at')
    search_fields = ('user__username', 'content', 'post__title')
    actions = ['approve_comments', 'disapprove_comments']
    
    def approve_comments(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f'{updated} bình luận đã được duyệt.')
    approve_comments.short_description = "Duyệt bình luận đã chọn"
    
    def disapprove_comments(self, request, queryset):
        updated = queryset.update(is_approved=False)
        self.message_user(request, f'{updated} bình luận đã bị ẩn.')
    disapprove_comments.short_description = "Ẩn bình luận đã chọn"


# ==================== ADVERTISEMENT ADMIN ====================
@admin.register(Advertisement)
class AdvertisementAdmin(admin.ModelAdmin):
    list_display = ('title', 'position', 'created_at')
    list_filter = ('position', 'created_at')
    search_fields = ('title',)
