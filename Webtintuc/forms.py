from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.utils.text import slugify
from django.core.exceptions import ValidationError  
from .models import Comment, Post


# ==================== AUTHENTICATION FORMS ====================
class RegisterForm(UserCreationForm):
    """Form đăng ký tài khoản"""
    full_name = forms.CharField(
        label='Họ và tên',
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Họ và tên'
        })
    )
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email'
        })
    )
    birth_date = forms.DateField(
        label='Ngày sinh',
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    GENDER_CHOICES = (
        ('', '-- Chọn giới tính --'),
        ('male', 'Nam'),
        ('female', 'Nữ'),
        ('other', 'Khác'),
    )
    gender = forms.ChoiceField(
        label='Giới tính',
        choices=GENDER_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    username = forms.CharField(
        label='Tên đăng nhập',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Tên đăng nhập'
        })
    )
    password1 = forms.CharField(
        label='Mật khẩu',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Mật khẩu'
        })
    )
    password2 = forms.CharField(
        label='Xác nhận mật khẩu',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Xác nhận mật khẩu'
        })
    )

    class Meta:
        model = User
        fields = ('full_name', 'birth_date', 'gender', 'email', 'username', 'password1', 'password2')


class LoginForm(forms.Form):
    """Form đăng nhập"""
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Tên đăng nhập'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Mật khẩu'
        })
    )



# ==================== POST FORMS ====================
class PostForm(forms.ModelForm):
    """Form tạo/chỉnh sửa bài viết (có ảnh tiêu đề)"""
    class Meta:
        model = Post
        fields = ('title', 'summary', 'content', 'category', 'status', 'post_type')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tiêu đề bài viết'}),
            'summary': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Tóm tắt ngắn gọn'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 10, 'placeholder': 'Nội dung bài viết'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'post_type': forms.Select(attrs={'class': 'form-control'}),
        }
    def clean_title(self):
        title = self.cleaned_data['title']
        slug = slugify(title)

        if not slug:
            raise ValidationError(
                'Tiêu đề bài viết không hợp lệ hoặc không tạo được đường dẫn URL.'
            )

        queryset = Post.objects.filter(slug=slug)

        if self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.exists():
            raise ValidationError(
                'Tiêu đề bài viết này đã tồn tại hoặc trùng đường dẫn tĩnh hệ thống.'
            )

        return title
class CommentForm(forms.ModelForm):
    """Form gửi bình luận"""
    content = forms.CharField(
        label='Bình luận',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Viết bình luận của bạn...',
            'rows': 4
        })
    )

    class Meta:
        model = Comment
        fields = ('content',)
    def clean_content(self):
        content = self.cleaned_data['content']

        blacklisted_words = [
            'mua ban',
            'hack',
            'casino',
            'rut tien',
            'banned',
            'quang cao',
        ]

        lowered_content = content.lower()

        for word in blacklisted_words:
            if word in lowered_content:
                raise ValidationError(
                    'Bình luận chứa ngôn từ không phù hợp hoặc quảng cáo spam.'
                )

        return content


# ==================== PROFILE FORM ====================
from .models import UserProfile

class ProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('avatar', 'bio', 'birth_date', 'phone', 'gender')
        widgets = {
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Giới thiệu bản thân...'}),
            'birth_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Số điện thoại'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'avatar': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
