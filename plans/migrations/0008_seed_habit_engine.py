from django.db import migrations


# Level requirement bands (consistency %, completion %, core-habit %)
def _band(n):
    if n <= 5:   return (80, 70, 75)
    if n <= 10:  return (80, 75, 80)
    if n <= 15:  return (85, 80, 85)
    return (90, 85, 90)


ACTIONS = [
    # slug, type, category, title, why, verif_type, source, metric, level_scaling
    ('walk_steps', 'core_habit', 'movement', 'Извърви крачките си за днес.',
     'Ходенето подобрява кръвообращението и сърдечно-съдовото здраве.',
     'sensor', 'healthkit/google_fit', 'steps', {'1': 2000, '5': 5000, '10': 8000, '20': 10000}),
    ('hydration', 'core_habit', 'hydration', 'Изпий чашите вода за днес.',
     'Хидратацията поддържа енергията и концентрацията.',
     'confirm', '', 'glasses', {'1': 4, '10': 6, '20': 8}),
    ('sleep', 'core_habit', 'sleep', 'Легни навреме за пълноценен сън.',
     'Добрият сън възстановява тялото и ума.',
     'sensor', 'healthkit/google_fit', 'hours', {'1': 6, '10': 7}),
    ('nutrition_meal', 'core_habit', 'nutrition', 'Приготви едно балансирано ястие.',
     'Балансираното хранене подхранва тялото ти.',
     'photo_ai', '', '', {}),
    ('meditate', 'growth_mission', 'mind', 'Отдели време за спокойствие.',
     'Кратката пауза успокоява ума и намалява стреса.',
     'timer', '', 'minutes', {'1': 5, '10': 10, '20': 15}),
    ('park_visit', 'growth_mission', 'movement', 'Прекарай време навън.',
     'Времето навън повдига настроението и енергията.',
     'location', '', 'minutes', {'1': 20}),
    ('call_friend', 'growth_mission', 'social', 'Обади се на близък човек.',
     'Връзките с хората са част от здравето.',
     'confirm', '', '', {}),
    ('stretch', 'growth_mission', 'movement', 'Разтегни се леко.',
     'Разтягането пази ставите гъвкави.',
     'timer', '', 'minutes', {'1': 3, '10': 5}),
]


def seed(apps, schema_editor):
    Level = apps.get_model('plans', 'Level')
    ActionDef = apps.get_model('plans', 'ActionDef')
    for n in range(1, 21):
        c, comp, core = _band(n)
        Level.objects.update_or_create(
            number=n,
            defaults=dict(min_days=14, consistency_req=c, completion_req=comp, core_habit_req=core),
        )
    for slug, typ, cat, title, why, vt, src, metric, scaling in ACTIONS:
        ActionDef.objects.update_or_create(
            slug=slug,
            defaults=dict(type=typ, category=cat, title=title, why=why,
                          verification_type=vt, verification_source=src,
                          metric=metric, level_scaling=scaling, is_active=True),
        )


def unseed(apps, schema_editor):
    apps.get_model('plans', 'Level').objects.all().delete()
    apps.get_model('plans', 'ActionDef').objects.filter(
        slug__in=[a[0] for a in ACTIONS]).delete()


class Migration(migrations.Migration):
    dependencies = [('plans', '0007_actiondef_level_userprogram_treestate_habitstability_and_more')]
    operations = [migrations.RunPython(seed, unseed)]
