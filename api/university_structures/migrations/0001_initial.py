# Generated by Django 3.2.7 on 2021-10-07 08:09

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Degree',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128, unique=True, validators=[django.core.validators.RegexValidator(message='Please enter a valid name.', regex='[A-ZА-Я][a-zа-я\\-\\s]+$')])),
            ],
        ),
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=128, unique=True, validators=[django.core.validators.RegexValidator(message='Please enter a valid title.', regex='[A-ZА-Я][a-zа-я\\-\\s]+$')])),
                ('description', models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Faculty',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=128, unique=True, validators=[django.core.validators.RegexValidator(message='Please enter a valid title.', regex='[A-ZА-Я][a-zа-я\\-\\s]+$')])),
                ('description', models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Position',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128, unique=True, validators=[django.core.validators.RegexValidator(message='Please enter a valid name.', regex='[A-ZА-Я][a-zа-я\\-\\s]+$')])),
            ],
        ),
        migrations.CreateModel(
            name='Speciality',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=128, unique=True, validators=[django.core.validators.RegexValidator(message='Please enter a valid title.', regex='[A-ZА-Я][a-zа-я\\-\\s]+$')])),
                ('code', models.PositiveSmallIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=5, validators=[django.core.validators.RegexValidator(message='Please enter a valid group name.', regex='[А-Я][А-Я]-[0-9][0-9]$')])),
                ('study_year', models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(6)])),
                ('department', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='university_structures.department')),
                ('speciality', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='university_structures.speciality')),
            ],
        ),
        migrations.AddField(
            model_name='department',
            name='faculty',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='university_structures.faculty'),
        ),
    ]
