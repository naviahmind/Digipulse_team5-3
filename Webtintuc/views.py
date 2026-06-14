from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Post, Category, Comment, Reaction, UserProfile, CategoryFollow, Notification, Tag, Advertisement
from .forms import RegisterForm, LoginForm, CommentForm, PostForm, ProfileForm
from django.utils.text import slugify


# ==================== HELPER: ROLE CHECK ====================
def is_author(user):
    """Tác giả hoặc admin đều có thể viết bài"""
    try:
        return user.profile.role in ('author', 'admin') or user.is_staff
    except Exception:
        return user.is_staff

def is_admin_role(user):
    """Kiểm tra vai trò admin (superuser hoặc profile.role == admin)"""
    try:
        return user.is_superuser or user.profile.role == 'admin'
    except Exception:
        return user.is_superuser


# ==================== AUTO-CREATE PROFILE ====================
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)


# ==================== CONTEXT HELPER ====================
def get_active_ads():
    """Trả về queryset quảng cáo đang hoạt động và còn trong thời hạn."""
    from django.utils import timezone
    today = timezone.now().date()
    return Advertisement.objects.filter(
        is_active=True,
    ).filter(
        models.Q(start_date__isnull=True) | models.Q(start_date__lte=today)
    ).filter(
        models.Q(end_date__isnull=True) | models.Q(end_date__gte=today)
    )

def get_base_context(request=None):
    active_ads = get_active_ads()
    ctx = {
        'categories': Category.objects.filter(category_type='news'),
        'header_ads':     active_ads.filter(position='header'),
        'sidebar_ads':    active_ads.filter(position='sidebar'),
        'footer_ads':     active_ads.filter(position='footer'),
        'in_article_ads': active_ads.filter(position='in_article'),
    }
    if request and request.user.is_authenticated:
        ctx['unread_count'] = Notification.objects.filter(user=request.user, is_read=False).count()
    return ctx


# ==================== AUTH VIEWS ====================
def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            # Tách họ và tên thành first_name / last_name
            full_name = form.cleaned_data.get('full_name', '').strip()
            parts = full_name.rsplit(' ', 1)
            if len(parts) == 2:
                user.first_name, user.last_name = parts[0], parts[1]
            else:
                user.first_name = full_name
            user.save()
            # Lưu thêm thông tin vào UserProfile
            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.birth_date = form.cleaned_data.get('birth_date')
            profile.gender = form.cleaned_data.get('gender')
            profile.save()
            login(request, user)
            return redirect('webtintuc:index')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {**get_base_context(request), 'form': form})


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(request, username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            if user:
                login(request, user)
                return redirect(request.GET.get('next', 'webtintuc:index'))
            form.add_error(None, 'Tên đăng nhập hoặc mật khẩu không đúng')
    else:
        form = LoginForm()
    return render(request, 'login.html', {**get_base_context(request), 'form': form})


def logout_view(request):
    logout(request)
    return redirect('webtintuc:index')


# ==================== MAIN VIEWS ====================
def index(request):
    featured_post = Post.objects.filter(status='published').order_by('-views_count').first()
    latest_posts = Post.objects.filter(status='published').order_by('-published_at')[:8]
    trending_posts = Post.objects.filter(status='published').order_by('-views_count')[:4]
    homepage_ads = get_active_ads().filter(position='homepage')
    return render(request, 'trang_chu.html', {
        **get_base_context(request),
        'featured_post': featured_post,
        'latest_posts': latest_posts,
        'trending_posts': trending_posts,
        'homepage_ads': homepage_ads,
    })


def latest_news(request):
    """Trang Mới Nhất – tất cả bài viết sắp xếp theo ngày đăng mới nhất"""
    posts = Post.objects.filter(status='published').order_by('-published_at')
    return render(request, 'latest_news.html', {
        **get_base_context(request),
        'posts': posts,
    })


def trending_news(request):
    """Trang Tin Nóng – bài viết có lượt xem nhiều nhất trong 24h qua"""
    from django.utils import timezone
    import datetime
    since = timezone.now() - datetime.timedelta(hours=24)
    posts = Post.objects.filter(
        status='published',
        published_at__gte=since
    ).order_by('-views_count')
    # Nếu trong 24h không đủ bài, lấy thêm bài ngoài 24h bù vào (tối đa 20)
    if posts.count() < 5:
        posts = Post.objects.filter(status='published').order_by('-views_count')[:20]
    return render(request, 'trending_news.html', {
        **get_base_context(request),
        'posts': posts,
        'is_24h': True,
    })


def most_viewed(request):
    """Trang Xem Nhiều – bài viết có tổng lượt xem nhiều nhất mọi thời gian"""
    posts = Post.objects.filter(status='published').order_by('-views_count')
    return render(request, 'most_viewed.html', {
        **get_base_context(request),
        'posts': posts,
    })


def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug, status='published')
    post.views_count += 1
    post.save(update_fields=['views_count'])

    related_posts = Post.objects.filter(category=post.category, status='published').exclude(id=post.id)[:3]
    comments = Comment.objects.filter(post=post, is_approved=True).order_by('created_at')

    # Reaction của user hiện tại
    user_reaction = None
    if request.user.is_authenticated:
        try:
            user_reaction = Reaction.objects.get(user=request.user, post=post).reaction_type
        except Reaction.DoesNotExist:
            pass

    comment_form = None
    if request.user.is_authenticated:
        if request.method == 'POST' and 'comment' in request.POST:
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                c = comment_form.save(commit=False)
                c.post = post
                c.user = request.user
                c.save()
                return redirect('webtintuc:post_detail', slug=post.slug)
        else:
            comment_form = CommentForm()

    return render(request, 'chi-tiet-tin.html', {
        **get_base_context(request),
        'post': post,
        'related_posts': related_posts,
        'comments': comments,
        'comment_form': comment_form,
        'user_reaction': user_reaction,
        'like_count': post.like_count(),
        'dislike_count': post.dislike_count(),
    })


# ==================== COMMENT: EDIT / DELETE ====================
@login_required(login_url='webtintuc:login')
def edit_comment(request, comment_id):
    """Người dùng sửa bình luận của chính mình"""
    comment = get_object_or_404(Comment, id=comment_id)
    if comment.user != request.user:
        return redirect('webtintuc:post_detail', slug=comment.post.slug)

    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
        return redirect('webtintuc:post_detail', slug=comment.post.slug)

    return redirect('webtintuc:post_detail', slug=comment.post.slug)


@login_required(login_url='webtintuc:login')
def delete_comment(request, comment_id):
    """Người dùng xóa bình luận của chính mình, hoặc admin xóa bất kỳ bình luận nào"""
    comment = get_object_or_404(Comment, id=comment_id)
    if (comment.user == request.user or request.user.is_staff) and request.method == 'POST':
        post_slug = comment.post.slug
        comment.delete()
        return redirect('webtintuc:post_detail', slug=post_slug)
    return redirect('webtintuc:post_detail', slug=comment.post.slug)


def search_posts(request):
    query = request.GET.get('q', '').strip()
    posts = Post.objects.filter(status='published', title__icontains=query).order_by('-published_at') if query else []
    return render(request, 'search_results.html', {**get_base_context(request), 'query': query, 'posts': posts})


def category_posts(request, slug):
    category = get_object_or_404(Category, slug=slug)
    posts = Post.objects.filter(category=category, status='published').order_by('-published_at')
    is_following = False
    if request.user.is_authenticated:
        is_following = CategoryFollow.objects.filter(user=request.user, category=category).exists()
    return render(request, 'category_news.html', {
        **get_base_context(request),
        'category': category,
        'posts': posts,
        'is_following': is_following,
    })


def category_news(request, slug):
    category = get_object_or_404(Category, slug=slug)
    posts = Post.objects.filter(category=category, status='published').order_by('-published_at')
    data = [{'title': p.title, 'slug': p.slug, 'published_at': p.published_at.strftime('%Y-%m-%d %H:%M'), 'views_count': p.views_count} for p in posts]
    return JsonResponse({'posts': data})


def chinh_sach(request):
    return render(request, 'chinh_sach.html', get_base_context(request))

def quang_cao(request):
    return render(request, 'quang_cao.html', get_base_context(request))

def huong_dan(request):
    return render(request, 'huong_dan.html', get_base_context(request))

def faq(request):
    return render(request, 'faq.html', get_base_context(request))


# ==================== REACTION (LIKE/DISLIKE) ====================
@login_required(login_url='webtintuc:login')
def react_post(request, slug):
    """AJAX: Like hoặc Dislike bài viết"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    post = get_object_or_404(Post, slug=slug)
    reaction_type = request.POST.get('type')  # 'like' hoặc 'dislike'
    if reaction_type not in ('like', 'dislike'):
        return JsonResponse({'error': 'Invalid type'}, status=400)

    existing = Reaction.objects.filter(user=request.user, post=post).first()
    if existing:
        if existing.reaction_type == reaction_type:
            existing.delete()   # bấm lại → bỏ react
            user_reaction = None
        else:
            existing.reaction_type = reaction_type  # đổi từ like → dislike hoặc ngược lại
            existing.save()
            user_reaction = reaction_type
    else:
        Reaction.objects.create(user=request.user, post=post, reaction_type=reaction_type)
        user_reaction = reaction_type

    return JsonResponse({
        'like_count': post.like_count(),
        'dislike_count': post.dislike_count(),
        'user_reaction': user_reaction,
    })


# ==================== FOLLOW CATEGORY ====================
@login_required(login_url='webtintuc:login')
def follow_category(request, slug):
    """AJAX: Follow/Unfollow danh mục"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    category = get_object_or_404(Category, slug=slug)
    obj, created = CategoryFollow.objects.get_or_create(user=request.user, category=category)
    if not created:
        obj.delete()
        return JsonResponse({'following': False, 'message': f'Đã bỏ theo dõi "{category.name}"'})
    return JsonResponse({'following': True, 'message': f'Đang theo dõi "{category.name}"'})


# ==================== NOTIFICATIONS ====================
@login_required(login_url='webtintuc:login')
def notifications(request):
    """Trang xem tất cả thông báo"""
    notifs = Notification.objects.filter(user=request.user).order_by('-created_at')[:50]
    # Đánh dấu tất cả là đã đọc
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return render(request, 'notifications.html', {**get_base_context(request), 'notifications': notifs})


@login_required(login_url='webtintuc:login')
def notifications_api(request):
    """AJAX polling: trả về số thông báo chưa đọc + 5 cái mới nhất"""
    notifs = Notification.objects.filter(user=request.user).order_by('-created_at')[:5]
    unread = Notification.objects.filter(user=request.user, is_read=False).count()
    data = [{'message': n.message, 'post_slug': n.post.slug if n.post else '', 'is_read': n.is_read, 'created_at': n.created_at.strftime('%d/%m %H:%M')} for n in notifs]
    return JsonResponse({'unread': unread, 'notifications': data})


# ==================== USER PROFILE ====================
def user_profile(request, username):
    """Trang thông tin công khai của một user"""
    profile_user = get_object_or_404(User, username=username)
    profile, _ = UserProfile.objects.get_or_create(user=profile_user)
    comments = Comment.objects.filter(user=profile_user, is_approved=True).select_related('post').order_by('-created_at')[:20]
    follows = CategoryFollow.objects.filter(user=profile_user).select_related('category')
    return render(request, 'user_profile.html', {
        **get_base_context(request),
        'profile_user': profile_user,
        'profile': profile,
        'comments': comments,
        'follows': follows,
    })


@login_required(login_url='webtintuc:login')
def edit_profile(request):
    """Trang chỉnh sửa profile của chính mình"""
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('webtintuc:user_profile', username=request.user.username)
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'edit_profile.html', {**get_base_context(request), 'form': form})


# ==================== AUTHOR/ADMIN: CREATE/EDIT POST ====================
@login_required(login_url='webtintuc:login')
def create_post(request):
    if not is_author(request.user):
        return redirect('webtintuc:index')
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            # Tác giả (không phải admin) chỉ lưu nháp, chờ duyệt
            if not is_admin_role(request.user) and not request.user.is_staff:
                post.status = 'draft'
            post.save()
            return redirect('webtintuc:my_posts')
    else:
        form = PostForm()
    return render(request, 'create_post.html', {**get_base_context(request), 'form': form})


@login_required(login_url='webtintuc:login')
def edit_post(request, slug):
    post = get_object_or_404(Post, slug=slug)
    is_admin = is_admin_role(request.user) or request.user.is_staff
    # Tác giả chỉ được sửa bài của chính mình; admin sửa tất cả
    if not is_author(request.user):
        return redirect('webtintuc:index')
    if not is_admin and post.author != request.user:
        return redirect('webtintuc:my_posts')
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            updated = form.save(commit=False)
            # Tác giả (không phải admin) không được tự publish
            if not is_admin:
                updated.status = 'draft'
            updated.save()
            form.save_m2m()
            return redirect('webtintuc:my_posts')
    else:
        form = PostForm(instance=post)
    return render(request, 'create_post.html', {**get_base_context(request), 'form': form, 'post': post, 'is_admin': is_admin})


@login_required(login_url='webtintuc:login')
def delete_post(request, slug):
    post = get_object_or_404(Post, slug=slug)
    is_admin = is_admin_role(request.user) or request.user.is_staff
    if not is_author(request.user):
        return redirect('webtintuc:index')
    # Tác giả chỉ được xóa bài của chính mình
    if not is_admin and post.author != request.user:
        return redirect('webtintuc:my_posts')
    if request.method == 'POST':
        post.delete()
        return redirect('webtintuc:my_posts')
    return redirect('webtintuc:my_posts')


@login_required(login_url='webtintuc:login')
def add_category_ajax(request):
    """AJAX: Thêm danh mục mới – chỉ admin mới được phép"""
    if not is_admin_role(request.user):
        return JsonResponse({'error': 'Forbidden'}, status=403)
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    name = request.POST.get('name', '').strip()
    if not name:
        return JsonResponse({'error': 'Tên danh mục không được để trống'}, status=400)
    slug = slugify(name)
    if not slug:
        return JsonResponse({'error': 'Tên danh mục không hợp lệ'}, status=400)
    category, created = Category.objects.get_or_create(slug=slug, defaults={'name': name})
    return JsonResponse({'id': category.id, 'name': category.name, 'created': created})


@login_required(login_url='webtintuc:login')
def add_tag_ajax(request):
    """AJAX: Thêm tag mới nhanh từ trang tạo bài viết"""
    if not is_author(request.user):
        return JsonResponse({'error': 'Forbidden'}, status=403)
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    name = request.POST.get('name', '').strip()
    if not name:
        return JsonResponse({'error': 'Tên tag không được để trống'}, status=400)
    slug = slugify(name)
    if not slug:
        return JsonResponse({'error': 'Tên tag không hợp lệ'}, status=400)
    tag, created = Tag.objects.get_or_create(slug=slug, defaults={'name': name})
    return JsonResponse({'id': tag.id, 'name': tag.name, 'created': created})


@login_required(login_url='webtintuc:login')
def my_posts(request):
    if not is_author(request.user):
        return redirect('webtintuc:index')
    # Admin/staff thấy tất cả bài; author chỉ thấy bài của mình
    if is_admin_role(request.user):
        posts = Post.objects.all().order_by('-created_at')
    else:
        posts = Post.objects.filter(author=request.user).order_by('-created_at')
    return render(request, 'my_posts.html', {**get_base_context(request), 'posts': posts})


# ==================== ADMIN: USER MANAGEMENT ====================
@login_required(login_url='webtintuc:login')
def manage_users(request):
    """Trang quản lý tài khoản người dùng (chỉ superuser hoặc admin role)"""
    if not is_admin_role(request.user):
        return redirect('webtintuc:index')

    query = request.GET.get('q', '').strip()
    role_filter = request.GET.get('role', '').strip()
    status_filter = request.GET.get('status', '').strip()

    from django.db.models import Q

    users = User.objects.select_related('profile').order_by('-date_joined')

    if query:
        users = users.filter(
            Q(username__icontains=query) |
            Q(email__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        )

    if role_filter == 'admin':
        # Admin = superuser HOẶC profile.role == 'admin'
        users = users.filter(Q(is_superuser=True) | Q(profile__role='admin'))
    elif role_filter == 'author':
        # Author = profile.role == 'author' nhưng không phải superuser
        users = users.filter(profile__role='author', is_superuser=False)
    elif role_filter == 'member':
        # Member = không phải superuser, không phải author, không phải admin role
        users = users.filter(
            is_superuser=False
        ).exclude(
            Q(profile__role='author') | Q(profile__role='admin')
        )

    if status_filter == 'active':
        users = users.filter(is_active=True)
    elif status_filter == 'locked':
        users = users.filter(is_active=False)

    total_users = User.objects.count()
    total_active = User.objects.filter(is_active=True).count()
    total_locked = User.objects.filter(is_active=False).count()
    total_admins = User.objects.filter(is_superuser=True).count()
    total_authors = UserProfile.objects.filter(role='author').count()

    return render(request, 'manage_users.html', {
        **get_base_context(request),
        'users': users,
        'query': query,
        'role_filter': role_filter,
        'status_filter': status_filter,
        'total_users': total_users,
        'total_active': total_active,
        'total_locked': total_locked,
        'total_admins': total_admins,
        'total_authors': total_authors,
    })


@login_required(login_url='webtintuc:login')
def toggle_user_active(request, user_id):
    if not is_admin_role(request.user):
        return redirect('webtintuc:index')
    target = get_object_or_404(User, id=user_id)
    if request.method == 'POST' and target != request.user:
        target.is_active = not target.is_active
        target.save(update_fields=['is_active'])
    return redirect('webtintuc:manage_users')


@login_required(login_url='webtintuc:login')
def toggle_user_admin(request, user_id):
    if not request.user.is_superuser:
        return redirect('webtintuc:index')
    target = get_object_or_404(User, id=user_id)
    if request.method == 'POST' and target != request.user:
        new_status = not target.is_superuser
        target.is_superuser = new_status
        target.is_staff = new_status
        target.save(update_fields=['is_superuser', 'is_staff'])
        # Cập nhật role trong profile
        profile, _ = UserProfile.objects.get_or_create(user=target)
        profile.role = 'admin' if new_status else 'user'
        profile.save()
    return redirect('webtintuc:manage_users')


@login_required(login_url='webtintuc:login')
def set_user_role(request, user_id):
    """Đặt vai trò user / author / admin cho người dùng"""
    if not is_admin_role(request.user):
        return redirect('webtintuc:index')
    target = get_object_or_404(User, id=user_id)
    if request.method == 'POST' and target != request.user:
        new_role = request.POST.get('role', 'user')
        if new_role not in ('user', 'author', 'admin'):
            return redirect('webtintuc:manage_users')
        profile, _ = UserProfile.objects.get_or_create(user=target)
        profile.role = new_role
        profile.save()
        # Đồng bộ is_staff / is_superuser
        if new_role == 'admin':
            target.is_staff = True
            target.is_superuser = True
        elif new_role == 'author':
            target.is_staff = True
            target.is_superuser = False
        else:
            target.is_staff = False
            target.is_superuser = False
        target.save(update_fields=['is_staff', 'is_superuser'])
    return redirect('webtintuc:manage_users')


@login_required(login_url='webtintuc:login')
def delete_user(request, user_id):
    if not is_admin_role(request.user):
        return redirect('webtintuc:index')
    target = get_object_or_404(User, id=user_id)
    if request.method == 'POST' and target != request.user and not target.is_superuser:
        target.delete()
    return redirect('webtintuc:manage_users')


@login_required(login_url='webtintuc:login')
def reset_user_password(request, user_id):
    if not is_admin_role(request.user):
        return redirect('webtintuc:index')
    target = get_object_or_404(User, id=user_id)
    if request.method == 'POST' and target != request.user:
        new_password = request.POST.get('new_password', '').strip()
        if len(new_password) >= 6:
            target.set_password(new_password)
            target.save()
    return redirect('webtintuc:manage_users')


# ==================== ADMIN: ADVERTISEMENT MANAGEMENT ====================
@login_required(login_url='webtintuc:login')
def manage_ads(request):
    """Trang quản lý quảng cáo (chỉ admin)"""
    if not is_admin_role(request.user):
        return redirect('webtintuc:index')
    ads = Advertisement.objects.all().order_by('-created_at')
    return render(request, 'manage_ads.html', {
        **get_base_context(request),
        'ads': ads,
        'position_choices': Advertisement.POSITION_CHOICES,
    })


@login_required(login_url='webtintuc:login')
def create_ad(request):
    if not is_admin_role(request.user):
        return redirect('webtintuc:index')
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        position = request.POST.get('position', 'sidebar')
        link_url = request.POST.get('link_url', '').strip()
        content = request.POST.get('content', '').strip()
        start_date = request.POST.get('start_date') or None
        end_date = request.POST.get('end_date') or None
        image = request.FILES.get('image')
        if title:
            ad = Advertisement(
                title=title, position=position,
                link_url=link_url or None,
                content=content or None,
                start_date=start_date, end_date=end_date,
                is_active=True,
            )
            if image:
                ad.image = image
            ad.save()
    return redirect('webtintuc:manage_ads')


@login_required(login_url='webtintuc:login')
def edit_ad(request, ad_id):
    if not is_admin_role(request.user):
        return redirect('webtintuc:index')
    ad = get_object_or_404(Advertisement, id=ad_id)
    if request.method == 'POST':
        ad.title = request.POST.get('title', ad.title).strip()
        ad.position = request.POST.get('position', ad.position)
        ad.link_url = request.POST.get('link_url', '').strip() or None
        ad.start_date = request.POST.get('start_date') or None
        ad.end_date = request.POST.get('end_date') or None
        ad.is_active = 'is_active' in request.POST
        if request.FILES.get('image'):
            ad.image = request.FILES['image']
        ad.save()
        return redirect('webtintuc:manage_ads')
    return render(request, 'edit_ad.html', {
        **get_base_context(request),
        'ad': ad,
        'position_choices': Advertisement.POSITION_CHOICES,
    })


@login_required(login_url='webtintuc:login')
def delete_ad(request, ad_id):
    if not is_admin_role(request.user):
        return redirect('webtintuc:index')
    ad = get_object_or_404(Advertisement, id=ad_id)
    if request.method == 'POST':
        ad.delete()
    return redirect('webtintuc:manage_ads')


@login_required(login_url='webtintuc:login')
def toggle_ad(request, ad_id):
    if not is_admin_role(request.user):
        return JsonResponse({'error': 'Forbidden'}, status=403)
    ad = get_object_or_404(Advertisement, id=ad_id)
    if request.method == 'POST':
        ad.is_active = not ad.is_active
        ad.save(update_fields=['is_active'])
        return JsonResponse({'is_active': ad.is_active})
    return JsonResponse({'error': 'Method not allowed'}, status=405)
