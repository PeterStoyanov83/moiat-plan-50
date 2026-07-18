from django.db import migrations

# slug -> difficulty, duration_min, contraindications, weather_adaptations, alternatives
META = {
    'walk_steps':     (2, 20, ['severe_joint_pain'], {'rain': 'march_indoors', 'heat': 'walk_early_or_evening'}, ['stretch']),
    'hydration':      (1, 1,  [], {}, []),
    'sleep':          (2, None, [], {}, []),
    'nutrition_meal': (2, 30, [], {}, []),
    'meditate':       (1, 10, [], {}, ['stretch']),
    'park_visit':     (2, 20, ['severe_joint_pain'], {'rain': 'indoor_plants_or_window'}, ['stretch']),
    'call_friend':    (1, 10, [], {}, []),
    'stretch':        (1, 5,  ['acute_injury'], {}, ['meditate']),
}


def backfill(apps, schema_editor):
    ActionDef = apps.get_model('plans', 'ActionDef')
    for slug, (diff, dur, contra, weather, alts) in META.items():
        ActionDef.objects.filter(slug=slug).update(
            difficulty=diff, duration_min=dur, contraindications=contra,
            weather_adaptations=weather, alternatives=alts,
        )


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [('plans', '0009_actiondef_alternatives_actiondef_contraindications_and_more')]
    operations = [migrations.RunPython(backfill, noop)]
