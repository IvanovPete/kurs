# Generated manually to add missing password field
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("leads", "0004_user_delete_lead"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="password",
            field=models.CharField(blank=True, max_length=128, null=True, verbose_name="Пароль"),
        ),
    ]
