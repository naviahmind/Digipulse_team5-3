from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Webtintuc', '0005_delete_contactmessage_alter_post_summary_and_more'),
    ]

    operations = [
        # Add role field to UserProfile
        migrations.AddField(
            model_name='userprofile',
            name='role',
            field=models.CharField(
                choices=[('user', 'Người dùng'), ('author', 'Tác giả'), ('admin', 'Quản trị viên')],
                default='user',
                max_length=10
            ),
        ),
        # Update Advertisement model: rename banner_url to link_url, add new fields
        migrations.RenameField(
            model_name='advertisement',
            old_name='banner_url',
            new_name='link_url',
        ),
        migrations.AlterField(
            model_name='advertisement',
            name='link_url',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='advertisement',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='ads/'),
        ),
        migrations.AddField(
            model_name='advertisement',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='advertisement',
            name='start_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='advertisement',
            name='end_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='advertisement',
            name='click_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='advertisement',
            name='position',
            field=models.CharField(
                choices=[
                    ('header', 'Header'),
                    ('sidebar', 'Sidebar'),
                    ('footer', 'Footer'),
                    ('in_article', 'Trong bài viết'),
                ],
                max_length=20
            ),
        ),
    ]
