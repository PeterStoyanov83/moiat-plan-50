from django.db import migrations

# Knowledge Engine (bos/engines/02-knowledge-engine.md): grow the library beyond the
# 8 starters. Every action carries FULL metadata (Constitution: "no action without
# metadata", "always explain WHY"). All new actions are growth_missions — the daily
# engine shows the 4 core habits first, so new cores would starve variety. Only
# `severe_joint_pain` / `acute_injury` contraindications are used, since those are the
# only tags daily.py::user_contraindications() can infer today.
#
# fields: slug, category, title, why, verif, metric, scaling, difficulty,
#         duration_min, contraindications, weather_adaptations, alternatives
M = 'growth_mission'
ACTIONS = [
    # --- movement -----------------------------------------------------------
    ('stairs_walk', 'movement', 'Изкачи едно стълбище пеша.',
     'Стълбите укрепват краката и сърцето.', 'confirm', '', {}, 2, 5,
     ['severe_joint_pain'], {}, ['stretch']),
    ('morning_walk', 'movement', 'Излез на кратка сутрешна разходка.',
     'Свежият въздух събужда тялото и повдига настроението.', 'location', 'minutes',
     {'1': 10, '10': 20}, 2, 15, ['severe_joint_pain'],
     {'rain': 'march_indoors', 'heat': 'walk_early_or_evening', 'cold': 'dress_warm_go_shorter'},
     ['chair_exercises', 'stretch']),
    ('dance_song', 'movement', 'Потанцувай на любима песен.',
     'Танцът раздвижва тялото и радва сърцето.', 'timer', 'minutes', {'1': 3, '10': 5},
     1, 5, [], {}, ['stretch']),
    ('garden_time', 'movement', 'Погрижи се за растение или градина.',
     'Градинарството съчетава леко движение и спокойствие.', 'confirm', '', {}, 2, 20,
     ['severe_joint_pain'], {'rain': 'tend_indoor_plants'}, ['stretch']),
    ('chair_exercises', 'movement', 'Направи няколко упражнения седнал на стол.',
     'Леките упражнения пазят мускулите активни — без натоварване на ставите.',
     'timer', 'minutes', {'1': 5, '10': 8}, 1, 8, [], {}, ['stretch']),
    ('balance_practice', 'movement', 'Постой на един крак, докато чакаш нещо.',
     'Балансът намалява риска от падане.', 'confirm', '', {}, 1, 2,
     ['acute_injury'], {}, ['chair_exercises']),
    ('neck_shoulder_roll', 'movement', 'Раздвижи бавно врата и раменете си.',
     'Разтоварва напрежението от седене.', 'timer', 'minutes', {'1': 2}, 1, 3,
     [], {}, ['stretch']),
    # --- nutrition ----------------------------------------------------------
    ('add_vegetable', 'nutrition', 'Добави зеленчук към едно хранене.',
     'Зеленчуците дават витамини и фибри.', 'photo_ai', '', {}, 1, 5, [], {},
     ['nutrition_meal']),
    ('eat_fruit', 'nutrition', 'Изяж парче плод днес.',
     'Плодовете са естествен източник на енергия.', 'confirm', '', {}, 1, 2, [], {}, []),
    ('home_cooked', 'nutrition', 'Сготви си домашно ястие.',
     'Домашната храна е по-питателна и щадяща.', 'photo_ai', '', {}, 2, 30, [], {},
     ['add_vegetable', 'nutrition_meal']),
    ('less_sugar', 'nutrition', 'Пропусни захарта в едно питие днес.',
     'По-малко захар държи енергията стабилна.', 'confirm', '', {}, 2, 1, [], {}, []),
    ('fish_meal', 'nutrition', 'Хапни риба вместо месо днес.',
     'Рибата съдържа полезни за сърцето мазнини.', 'photo_ai', '', {}, 2, 30, [], {},
     ['nutrition_meal']),
    ('mindful_breakfast', 'nutrition', 'Започни деня със спокойна закуска.',
     'Добрата закуска зарежда деня.', 'confirm', '', {}, 1, 15, [], {}, []),
    ('warm_soup', 'nutrition', 'Стопли си купа супа.',
     'Супата топли и хидратира.', 'confirm', '', {}, 1, 15, [],
     {'cold': 'perfect_for_cold_days'}, []),
    # --- hydration ----------------------------------------------------------
    ('herbal_tea', 'hydration', 'Изпий чаша билков чай.',
     'Топлият чай успокоява и хидратира.', 'confirm', '', {}, 1, 5, [],
     {'cold': 'warms_you_up'}, ['hydration']),
    ('water_before_meal', 'hydration', 'Изпий чаша вода преди хранене.',
     'Водата преди ядене помага на храносмилането.', 'confirm', '', {}, 1, 1, [], {},
     ['hydration']),
    # --- sleep / wind-down --------------------------------------------------
    ('no_screen_bed', 'sleep', 'Остави телефона 30 минути преди сън.',
     'Без екрани заспиваш по-лесно.', 'timer', 'minutes', {'1': 30}, 2, 30, [], {},
     ['evening_stretch', 'meditate']),
    ('consistent_bedtime', 'sleep', 'Легни по едно и също време тази вечер.',
     'Редовният ритъм подобрява съня.', 'confirm', '', {}, 2, 1, [], {}, ['sleep']),
    ('evening_stretch', 'sleep', 'Разтегни се леко преди лягане.',
     'Лекото разтягане отпуска тялото за сън.', 'timer', 'minutes', {'1': 5}, 1, 5,
     ['acute_injury'], {}, ['meditate']),
    ('air_the_room', 'sleep', 'Проветри спалнята преди сън.',
     'Свежият въздух подобрява почивката.', 'confirm', '', {}, 1, 2, [], {}, []),
    # --- social -------------------------------------------------------------
    ('visit_someone', 'social', 'Посети близък човек или съсед.',
     'Личните срещи топлят сърцето.', 'confirm', '', {}, 2, 30, [], {}, ['call_friend']),
    ('write_message', 'social', 'Напиши съобщение на приятел.',
     'Малкото внимание поддържа връзките.', 'confirm', '', {}, 1, 5, [], {},
     ['call_friend']),
    ('help_someone', 'social', 'Помогни на някого с малко нещо.',
     'Да помагаш дава смисъл и радост.', 'confirm', '', {}, 1, 10, [], {}, []),
    ('share_meal', 'social', 'Хапни заедно с някого днес.',
     'Споделената храна сближава.', 'confirm', '', {}, 2, 30, [], {}, ['call_friend']),
    ('say_thanks', 'social', 'Кажи „благодаря" на някого днес.',
     'Благодарността укрепва отношенията.', 'confirm', '', {}, 1, 2, [], {}, []),
    # --- mind ---------------------------------------------------------------
    ('breathing', 'mind', 'Направи 5 бавни, дълбоки вдишвания.',
     'Дишането успокоява нервната система.', 'timer', 'minutes', {'1': 2, '10': 5}, 1, 3,
     [], {}, ['meditate']),
    ('gratitude_list', 'mind', 'Запиши три неща, за които си благодарен.',
     'Благодарността повдига настроението.', 'confirm', '', {}, 1, 5, [], {}, ['meditate']),
    ('read_book', 'mind', 'Прочети няколко страници от книга.',
     'Четенето поддържа ума буден.', 'timer', 'minutes', {'1': 10, '10': 20}, 1, 15,
     [], {}, []),
    ('listen_music', 'mind', 'Послушай любима музика.',
     'Музиката облекчава стреса.', 'timer', 'minutes', {'1': 5}, 1, 10, [], {}, []),
    ('nature_moment', 'mind', 'Погледай природата няколко минути.',
     'Природата успокоява ума.', 'confirm', '', {}, 1, 5, [],
     {'rain': 'watch_from_window'}, ['park_visit']),
    ('learn_something', 'mind', 'Научи едно ново нещо днес.',
     'Ученето пази ума пъргав.', 'confirm', '', {}, 2, 15, [], {}, []),
    ('journal', 'mind', 'Запиши как мина денят ти.',
     'Писането подрежда мислите.', 'timer', 'minutes', {'1': 5}, 1, 5, [], {}, []),
    ('digital_pause', 'mind', 'Отдели време без новини и екрани.',
     'Паузата от екрани зарежда ума.', 'timer', 'minutes', {'1': 30, '10': 60}, 2, 30,
     [], {}, ['meditate']),
    # --- financial ----------------------------------------------------------
    ('track_expense', 'financial', 'Запиши разходите си за днес.',
     'Прегледът на разходите носи спокойствие.', 'confirm', '', {}, 1, 5, [], {}, []),
    ('small_saving', 'financial', 'Задели малка сума настрани.',
     'Малките спестявания растат с времето.', 'confirm', '', {}, 1, 2, [], {}, []),
    ('no_spend_day', 'financial', 'Прекарай ден без излишни покупки.',
     'Съзнателното харчене намалява стреса.', 'confirm', '', {}, 2, 1, [], {}, []),
    ('review_subscription', 'financial', 'Провери един абонамент, който не ползваш.',
     'Отменените дребни разходи се събират.', 'confirm', '', {}, 2, 10, [], {}, []),
]


def seed(apps, schema_editor):
    ActionDef = apps.get_model('plans', 'ActionDef')
    for (slug, cat, title, why, vt, metric, scaling, diff, dur, contra, weather, alts) in ACTIONS:
        ActionDef.objects.update_or_create(
            slug=slug,
            defaults=dict(
                type=M, category=cat, title=title, why=why,
                verification_type=vt, verification_source='', metric=metric,
                level_scaling=scaling, difficulty=diff, duration_min=dur,
                contraindications=contra, weather_adaptations=weather,
                alternatives=alts, is_active=True,
            ),
        )


def unseed(apps, schema_editor):
    apps.get_model('plans', 'ActionDef').objects.filter(
        slug__in=[a[0] for a in ACTIONS]).delete()


class Migration(migrations.Migration):
    dependencies = [('plans', '0010_backfill_action_metadata')]
    operations = [migrations.RunPython(seed, unseed)]
