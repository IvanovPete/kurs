# Generated manually: add password field to User model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("leads", "0003_lead_age"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="password",
            field=models.CharField(
                blank=True, max_length=128, null=True, verbose_name="Пароль"
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="yandex_id",
            field=models.CharField(
                blank=True, max_length=100, null=True, unique=True, verbose_name="Яндекс ID"
            ),
        ),
    ]
