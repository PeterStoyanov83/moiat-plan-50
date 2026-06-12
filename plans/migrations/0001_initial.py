from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='QuestionnaireResponse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('age', models.IntegerField(verbose_name='Възраст')),
                ('gender', models.CharField(max_length=20, verbose_name='Пол')),
                ('height', models.IntegerField(verbose_name='Ръст (см)')),
                ('weight', models.IntegerField(verbose_name='Тегло (кг)')),
                ('working_status', models.CharField(max_length=50, verbose_name='Работен статус')),
                ('living_status', models.CharField(max_length=50, verbose_name='С кого живеете')),
                ('energy_level', models.IntegerField(verbose_name='Ниво на енергия (1-5)')),
                ('sleep_hours', models.IntegerField(verbose_name='Часове сън')),
                ('health_limitations', models.TextField(blank=True, verbose_name='Здравословни ограничения')),
                ('eating_frequency', models.CharField(max_length=50, verbose_name='Честота на хранене')),
                ('evening_meal_type', models.CharField(max_length=50, verbose_name='Вечерно хранене')),
                ('main_goal', models.CharField(max_length=50, verbose_name='Основна цел')),
                ('movement_level', models.CharField(max_length=50, verbose_name='Ниво на движение')),
                ('preferred_movement', models.CharField(max_length=50, verbose_name='Предпочитано движение')),
                ('joint_pain', models.CharField(max_length=20, verbose_name='Болки в ставите')),
                ('social_activity', models.CharField(max_length=50, verbose_name='Социална активност')),
                ('has_hobby', models.BooleanField(verbose_name='Има хоби')),
                ('ninety_day_goal', models.TextField(verbose_name='90-дневна цел')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Отговор от въпросник',
                'verbose_name_plural': 'Отговори от въпросник',
            },
        ),
        migrations.CreateModel(
            name='UserPlan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('profile_type', models.CharField(max_length=100, verbose_name='Тип профил')),
                ('profile_description', models.TextField(verbose_name='Описание на профила')),
                ('nutrition_plan', models.TextField(verbose_name='Хранителен план')),
                ('movement_plan', models.TextField(verbose_name='План за движение')),
                ('habits_plan', models.TextField(verbose_name='Ежедневни навици')),
                ('financial_habit', models.TextField(verbose_name='Финансов навик')),
                ('social_plan', models.TextField(verbose_name='Социален план')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('response', models.OneToOneField(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='plan',
                    to='plans.questionnaireresponse',
                )),
            ],
            options={
                'verbose_name': 'Личен план',
                'verbose_name_plural': 'Лични планове',
            },
        ),
        migrations.CreateModel(
            name='Feedback',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('clarity_score', models.IntegerField(verbose_name='Яснота (1-5)')),
                ('usefulness_score', models.IntegerField(verbose_name='Полезност (1-5)')),
                ('realistic_score', models.IntegerField(verbose_name='Реалистичност (1-5)')),
                ('would_use_again', models.BooleanField(verbose_name='Би използвал отново')),
                ('would_pay', models.BooleanField(verbose_name='Би платил')),
                ('suggested_price', models.CharField(blank=True, max_length=50, verbose_name='Предложена цена')),
                ('most_useful_part', models.TextField(blank=True, verbose_name='Най-полезната част')),
                ('improvement_suggestion', models.TextField(blank=True, verbose_name='Предложение за подобрение')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('response', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='feedbacks',
                    to='plans.questionnaireresponse',
                )),
            ],
            options={
                'verbose_name': 'Обратна връзка',
                'verbose_name_plural': 'Обратни връзки',
            },
        ),
    ]
