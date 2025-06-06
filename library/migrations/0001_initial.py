# Generated by Django 5.0.1 on 2024-08-17 17:13

import datetime
import django.contrib.auth.models
import django.contrib.auth.validators
import django.core.serializers.json
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Artist',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('artist', models.CharField(default='', max_length=255)),
                ('short_name', models.CharField(blank=True, max_length=6, null=True)),
                ('comment', models.TextField(blank=True, null=True)),
                ('olddb_id', models.IntegerField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Genre',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('genre', models.CharField(default='', max_length=255)),
                ('olddb_id', models.IntegerField(blank=True, null=True)),
            ],
            options={
                'ordering': ('genre',),
            },
        ),
        migrations.CreateModel(
            name='Label',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(default='', max_length=255)),
                ('contact_person', models.CharField(blank=True, max_length=80, null=True)),
                ('email', models.CharField(blank=True, max_length=80, null=True)),
                ('address', models.CharField(blank=True, max_length=80, null=True)),
                ('city', models.CharField(blank=True, max_length=80, null=True)),
                ('state', models.CharField(blank=True, max_length=2, null=True)),
                ('phone', models.CharField(blank=True, max_length=80, null=True)),
                ('comment', models.TextField(blank=True, null=True)),
                ('olddb_id', models.IntegerField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('djname', models.CharField(blank=True, max_length=40, null=True)),
                ('phone', models.CharField(blank=True, max_length=80, null=True)),
                ('email', models.EmailField(blank=True, max_length=255, null=True, verbose_name='email address')),
                ('date_trained', models.DateField(default=datetime.date.today, null=True)),
                ('auth_level', models.CharField(choices=[('none', 'None'), ('user', 'User'), ('exec', 'Exec'), ('admin', 'Admin')], default='user', max_length=5)),
                ('olddb_id', models.IntegerField(blank=True, null=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Album',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('album', models.CharField(default='', max_length=255)),
                ('year', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('date_added', models.DateField(default=datetime.date.today, null=True)),
                ('date_removed', models.DateField(blank=True, null=True)),
                ('status', models.CharField(blank=True, choices=[('Bin', 'Bin'), ('N&WC', 'N&WC (??)'), ('NIB', 'Not in bin'), ('TBR', 'To be reviewed'), ('OOB', 'Out of bin')], max_length=4, null=True)),
                ('format', models.IntegerField(blank=True, choices=[(12, 'LP'), (11, '12" vinyl'), (10, '10" vinyl'), (9, 'EP single'), (8, '7" vinyl'), (7, 'CD'), (14, 'Kassette'), (15, '7"'), (16, 'EP'), (17, 'Digital')], null=True)),
                ('olddb_id', models.IntegerField(blank=True, null=True)),
                ('artist', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='library.artist')),
                ('genre', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='library.genre')),
                ('label', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='library.label')),
            ],
            options={
                'ordering': ('-date_added', 'album'),
            },
        ),
        migrations.CreateModel(
            name='LibraryEntry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.IntegerField(choices=[(1, 'created'), (2, 'updated'), (3, 'deleted')], default=1)),
                ('action_time', models.DateTimeField(default=django.utils.timezone.now)),
                ('object_id', models.IntegerField(blank=True, null=True)),
                ('object_str', models.CharField(blank=True, max_length=255, null=True)),
                ('table', models.CharField(blank=True, choices=[('Album', 'Album'), ('Artist', 'Artist'), ('Label', 'Label'), ('Review', 'Review'), ('Genre', 'Genre'), ('Subgenre', 'Subgenre'), ('User', 'User')], max_length=16, null=True)),
                ('changed_fields', models.JSONField(blank=True, encoder=django.core.serializers.json.DjangoJSONEncoder, null=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-action_time',),
            },
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_added', models.DateTimeField(default=django.utils.timezone.now)),
                ('review', models.TextField(default='')),
                ('olddb_id', models.IntegerField(blank=True, null=True)),
                ('album', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='library.album')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-date_added',),
            },
        ),
        migrations.CreateModel(
            name='Subgenre',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subgenre', models.CharField(default='', max_length=255)),
                ('olddb_id', models.IntegerField(blank=True, null=True)),
                ('genre', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='library.genre')),
            ],
            options={
                'ordering': ('genre', 'subgenre'),
            },
        ),
        migrations.AddField(
            model_name='album',
            name='subgenre',
            field=models.ManyToManyField(blank=True, to='library.subgenre'),
        ),
    ]
