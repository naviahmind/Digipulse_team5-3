from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Webtintuc', '0006_userprofile_role_advertisement_updates'),
    ]

    operations = [
        # Thêm field content cho quảng cáo dạng văn bản (không cần ảnh)
        migrations.AddField(
            model_name='advertisement',
            name='content',
            field=models.TextField(
                blank=True,
                null=True,
                help_text='Nội dung quảng cáo (hiển thị khi không có ảnh)'
            ),
        ),
        # Thêm vị trí 'homepage' vào POSITION_CHOICES
        migrations.AlterField(
            model_name='advertisement',
            name='position',
            field=models.CharField(
                choices=[
                    ('homepage', 'Trang chủ'),
                    ('header', 'Header'),
                    ('sidebar', 'Sidebar'),
                    ('footer', 'Footer'),
                    ('in_article', 'Trong bài viết'),
                ],
                max_length=20
            ),
        ),
    ]
