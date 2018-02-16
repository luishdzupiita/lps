from django.db import models


class User(models.Model):
    id = models.AutoField(primary_key=True)

    username = models.CharField(max_length=32, null=True)
    password = models.CharField(max_length=32, null=True)

    created_at = models.DateTimeField(
        auto_now_add=True, db_index=True, null=True)
    updated_at = models.DateTimeField(
        auto_now=True, db_index=True, null=True)

    class Meta:
        db_table = 'user'
