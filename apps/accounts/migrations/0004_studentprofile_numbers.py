from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0003_alter_customuser_role_alter_otp_user"),
    ]

    operations = [
        # Add admission_number with a temporary default so existing rows don't fail
        migrations.AddField(
            model_name="studentprofile",
            name="admission_number",
            field=models.CharField(max_length=30, default="PENDING"),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="studentprofile",
            name="enrollment_number",
            field=models.CharField(max_length=30, default="PENDING"),
            preserve_default=False,
        ),
        # Add unique constraints AFTER populating (on fresh DBs they're fine as-is)
        migrations.AlterField(
            model_name="studentprofile",
            name="admission_number",
            field=models.CharField(max_length=30, unique=True),
        ),
        migrations.AlterField(
            model_name="studentprofile",
            name="enrollment_number",
            field=models.CharField(max_length=30, unique=True),
        ),
    ]
