from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Webtintuc', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='thumbnail',
            field=models.ImageField(
                blank=True,
                help_text='Ảnh tiêu đề bài viết',
                null=True,
                upload_to='thumbnails/'
            ),
        ),
        migrations.AlterField(
            model_name='comment',
            name='is_approved',
            field=models.BooleanField(default=True),
        ),
    ]
