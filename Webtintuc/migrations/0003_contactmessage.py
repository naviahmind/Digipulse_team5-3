from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Webtintuc', '0002_post_thumbnail_comment_is_approved'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContactMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('email', models.EmailField()),
                ('message_type', models.CharField(
                    choices=[('contact', 'Liên hệ'), ('feedback', 'Phản hồi'), ('bug', 'Báo cáo lỗi')],
                    default='contact', max_length=20
                )),
                ('subject', models.CharField(max_length=200)),
                ('content', models.TextField()),
                ('is_read', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Tin Nhắn',
                'verbose_name_plural': 'Tin Nhắn',
                'ordering': ['-created_at'],
            },
        ),
    ]
