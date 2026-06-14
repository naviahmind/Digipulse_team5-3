from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.utils import timezone


# ==================== CATEGORY MODEL ====================
class Category(models.Model):
    CATEGORY_TYPES = (
        ('news', 'Tin Tức'),
        ('blog', 'Blog'),
    )
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True, null=True)
    category_type = models.CharField(max_length=20, choices=CATEGORY_TYPES, default='news')
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


# ==================== TAG MODEL ====================
class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


# ==================== POST MODEL ====================
class Post(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Nháp'),
        ('published', 'Đã đăng'),
    )
    POST_TYPES = (
        ('news', 'Tin Tức'),
        ('blog', 'Blog'),
    )

    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    thumbnail = models.ImageField(upload_to='thumbnails/', null=True, blank=True)
    content = models.TextField()
    summary = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    tags = models.ManyToManyField(Tag, blank=True)
    views_count = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    post_type = models.CharField(max_length=20, choices=POST_TYPES, default='news')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-published_at', '-created_at']
        verbose_name = "Bài Viết"
        verbose_name_plural = "Bài Viết"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        was_draft = False
        if not is_new:
            try:
                old = Post.objects.get(pk=self.pk)
                was_draft = old.status == 'draft'
            except Post.DoesNotExist:
                pass

        if not self.slug:
            self.slug = slugify(self.title)
        if self.status == 'published' and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)

        # Tạo thông báo cho người follow danh mục khi bài được publish lần đầu
        if self.status == 'published' and (is_new or was_draft):
            followers = CategoryFollow.objects.filter(category=self.category).select_related('user')
            notifications = [
                Notification(
                    user=f.user,
                    post=self,
                    message=f'Bài viết mới trong "{self.category.name}": {self.title}',
                )
                for f in followers
            ]
            if notifications:
                Notification.objects.bulk_create(notifications)

    def like_count(self):
        return self.reactions.filter(reaction_type='like').count()

    def dislike_count(self):
        return self.reactions.filter(reaction_type='dislike').count()


# ==================== REACTION MODEL ====================
class Reaction(models.Model):
    REACTION_TYPES = (
        ('like', 'Like'),
        ('dislike', 'Dislike'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='reactions')
    reaction_type = models.CharField(max_length=10, choices=REACTION_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')  # mỗi user chỉ react 1 lần / bài

    def __str__(self):
        return f"{self.user.username} {self.reaction_type} {self.post.title}"


# ==================== COMMENT MODEL ====================
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    is_approved = models.BooleanField(default=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Bình Luận"
        verbose_name_plural = "Bình Luận"

    def __str__(self):
        return f"Comment của {self.user.username} trên {self.post.title}"


# ==================== USER PROFILE MODEL ====================
class UserProfile(models.Model):
    GENDER_CHOICES = (
        ('male', 'Nam'),
        ('female', 'Nữ'),
        ('other', 'Khác'),
    )
    ROLE_CHOICES = (
        ('user', 'Người dùng'),
        ('author', 'Tác giả'),
        ('admin', 'Quản trị viên'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    bio = models.TextField(blank=True, null=True)
    birth_date = models.DateField(null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')

    def __str__(self):
        return f"Profile của {self.user.username}"

    def get_avatar_url(self):
        if self.avatar:
            return self.avatar.url
        return None  # template sẽ dùng avatar mặc định


# ==================== CATEGORY FOLLOW MODEL ====================
class CategoryFollow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='category_follows')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='followers')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'category')

    def __str__(self):
        return f"{self.user.username} follows {self.category.name}"


# ==================== NOTIFICATION MODEL ====================
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True)
    message = models.CharField(max_length=300)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notif cho {self.user.username}: {self.message[:50]}"


# ==================== ADVERTISEMENT MODEL ====================
class Advertisement(models.Model):
    POSITION_CHOICES = (
        ('homepage', 'Trang chủ'),
        ('header', 'Header'),
        ('sidebar', 'Sidebar'),
        ('footer', 'Footer'),
        ('in_article', 'Trong bài viết'),
    )
    title = models.CharField(max_length=100)
    content = models.TextField(blank=True, null=True, help_text='Nội dung quảng cáo (hiển thị khi không có ảnh)')
    image = models.ImageField(upload_to='ads/', null=True, blank=True)
    link_url = models.URLField(blank=True, null=True)
    position = models.CharField(max_length=20, choices=POSITION_CHOICES)
    is_active = models.BooleanField(default=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    click_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
