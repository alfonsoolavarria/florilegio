from django.contrib.postgres.operations import UnaccentExtension
from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('main_florife', '0003_author_article_author'),
    ]

    operations = [
        UnaccentExtension(),
    ]
