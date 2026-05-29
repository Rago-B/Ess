from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("mail_client", "0005_pinnedemail"),
    ]

    operations = [
        migrations.AddField(
            model_name="pinnedemail",
            name="sender",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="pinnedemail",
            name="snippet",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="pinnedemail",
            name="subject",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterUniqueTogether(
            name="pinnedemail",
            unique_together={("uid", "folder")},
        ),
    ]
