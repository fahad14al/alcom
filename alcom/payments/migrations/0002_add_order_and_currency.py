from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0001_initial'),
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='order',
            field=models.ForeignKey(null=True, blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='payments', to='orders.order'),
        ),
        migrations.AddField(
            model_name='payment',
            name='currency',
            field=models.CharField(default='USD', max_length=10),
            preserve_default=False,
        ),
    ]
