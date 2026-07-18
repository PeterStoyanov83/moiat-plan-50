from django.db import migrations

# Knowledge Engine (bos/engines/02): grow the library to ~100 actions. All new
# actions are growth_missions with full metadata + why (Constitution). Uses the
# refined contraindication tags now inferrable by daily.py::user_contraindications()
# — severe_joint_pain, acute_injury, cardiac, balance_issues, respiratory.
# Weather adaptations are carried but not yet honored (deferred to a later version).
M = 'growth_mission'
# slug, category, title, why, verif, metric, scaling, difficulty, duration, contra, weather, alts
ACTIONS = [
    # --- movement -----------------------------------------------------------
    ('brisk_walk', 'movement', 'Разходи се с малко по-бърза крачка.',
     'По-бързото ходене засилва издръжливостта.', 'location', 'minutes', {'1': 10, '10': 20},
     3, 15, ['cardiac', 'respiratory', 'severe_joint_pain'], {'rain': 'march_indoors'},
     ['chair_exercises', 'stretch']),
    ('calf_raises', 'movement', 'Повдигни се на пръсти няколко пъти.',
     'Укрепва прасците и глезените.', 'timer', 'minutes', {'1': 2}, 1, 3,
     ['balance_issues'], {}, ['chair_exercises']),
    ('wall_pushups', 'movement', 'Направи лицеви опори до стена.',
     'Засилва нежно ръцете и раменете.', 'timer', 'minutes', {'1': 2, '10': 4}, 2, 5,
     ['acute_injury'], {}, ['chair_exercises']),
    ('gentle_squats', 'movement', 'Стани и седни от стол няколко пъти.',
     'Укрепва краката за по-лесно движение.', 'timer', 'minutes', {'1': 2, '10': 4}, 2, 5,
     ['severe_joint_pain', 'balance_issues'], {}, ['chair_exercises']),
    ('arm_circles', 'movement', 'Направи бавни кръгове с ръцете.',
     'Раздвижва раменете и подобрява обхвата.', 'timer', 'minutes', {'1': 2}, 1, 3,
     [], {}, ['stretch']),
    ('swim_or_pool', 'movement', 'Поплувай или се раздвижи във вода.',
     'Водата разтоварва ставите, докато тялото работи.', 'confirm', '', {}, 2, 30,
     [], {}, ['stretch']),
    ('bike_ride', 'movement', 'Покарай велосипед.',
     'Колоезденето е леко за ставите и добро за сърцето.', 'confirm', '', {}, 3, 20,
     ['acute_injury', 'balance_issues'], {'rain': 'stationary_or_skip'}, ['morning_walk']),
    ('housework_active', 'movement', 'Свърши активна домакинска работа.',
     'Домакинството също е движение.', 'confirm', '', {}, 1, 20, [], {}, ['stretch']),
    ('walk_after_meal', 'movement', 'Разходи се 10 минути след хранене.',
     'Кратката разходка помага на храносмилането.', 'location', 'minutes', {'1': 10}, 1, 10,
     ['severe_joint_pain'], {'rain': 'march_indoors'}, ['chair_exercises']),
    # --- nutrition ----------------------------------------------------------
    ('eat_greens', 'nutrition', 'Хапни листни зеленчуци днес.',
     'Зелените листа са богати на желязо и фибри.', 'photo_ai', '', {}, 1, 5, [], {},
     ['add_vegetable']),
    ('nuts_snack', 'nutrition', 'Хапни шепа ядки вместо сладко.',
     'Ядките дават здравословна енергия.', 'confirm', '', {}, 1, 2, [], {}, ['eat_fruit']),
    ('yogurt_daily', 'nutrition', 'Изяж кисело мляко днес.',
     'Киселото мляко подкрепя храносмилането.', 'confirm', '', {}, 1, 3, [], {}, []),
    ('reduce_salt', 'nutrition', 'Опитай ястие с по-малко сол.',
     'По-малко сол щади сърцето и бъбреците.', 'confirm', '', {}, 2, 1, [], {}, []),
    ('colorful_plate', 'nutrition', 'Направи чинията си шарена.',
     'Различните цветове носят различни витамини.', 'photo_ai', '', {}, 1, 10, [], {},
     ['add_vegetable']),
    ('slow_eating', 'nutrition', 'Яж бавно и се наслаждавай на храната.',
     'Бавното хранене помага на ситостта.', 'confirm', '', {}, 1, 15, [], {},
     ['mindful_breakfast']),
    ('portion_control', 'nutrition', 'Сипи си умерена порция.',
     'Умерените порции пазят лека тежест.', 'confirm', '', {}, 2, 5, [], {}, []),
    ('swap_snack', 'nutrition', 'Замени един снек с плод или зеленчук.',
     'Малката смяна прави разлика.', 'confirm', '', {}, 1, 2, [], {}, ['eat_fruit']),
    ('cook_batch', 'nutrition', 'Сготви за няколко дни напред.',
     'Готовата храна улеснява добрия избор.', 'photo_ai', '', {}, 2, 45, [], {},
     ['home_cooked']),
    # --- hydration ----------------------------------------------------------
    ('morning_water', 'hydration', 'Изпий чаша вода щом станеш.',
     'Водата сутрин събужда тялото.', 'confirm', '', {}, 1, 1, [], {}, ['hydration']),
    ('water_bottle', 'hydration', 'Носи бутилка вода със себе си.',
     'Под ръка пиеш повече.', 'confirm', '', {}, 1, 1, [], {}, ['hydration']),
    ('limit_soda', 'hydration', 'Пропусни газираните напитки днес.',
     'По-малко захар и повече бистрота.', 'confirm', '', {}, 2, 1, [], {}, ['herbal_tea']),
    ('fruit_infused_water', 'hydration', 'Добави резен плод във водата.',
     'Вкусната вода се пие по-леко.', 'confirm', '', {}, 1, 3, [], {}, ['hydration']),
    ('soup_broth', 'hydration', 'Изпий чаша топъл бульон.',
     'Бульонът хидратира и топли.', 'confirm', '', {}, 1, 10, [], {'cold': 'warms_you_up'},
     ['warm_soup']),
    ('water_sip_hourly', 'hydration', 'Пий по глътка вода на всеки час.',
     'Малко и често държи хидратацията.', 'confirm', '', {}, 1, 1, [], {}, ['hydration']),
    # --- sleep --------------------------------------------------------------
    ('dim_lights', 'sleep', 'Намали осветлението вечер.',
     'По-меката светлина подготвя за сън.', 'confirm', '', {}, 1, 2, [], {}, []),
    ('warm_bath', 'sleep', 'Вземи топла вана или душ вечер.',
     'Топлината отпуска тялото за сън.', 'confirm', '', {}, 1, 15, [], {}, ['evening_stretch']),
    ('no_caffeine_pm', 'sleep', 'Избягвай кафе следобед.',
     'Без кофеин заспиваш по-леко.', 'confirm', '', {}, 2, 1, [], {}, []),
    ('bedtime_reading', 'sleep', 'Прочети нещо спокойно преди сън.',
     'Четенето отпуска ума за сън.', 'timer', 'minutes', {'1': 10}, 1, 10, [], {},
     ['read_book']),
    ('gratitude_before_sleep', 'sleep', 'Спомни си едно хубаво нещо от деня.',
     'Добрите мисли носят спокоен сън.', 'confirm', '', {}, 1, 3, [], {}, ['gratitude_list']),
    ('consistent_wake', 'sleep', 'Стани по едно и също време.',
     'Редовното събуждане стабилизира ритъма.', 'confirm', '', {}, 2, 1, [], {},
     ['consistent_bedtime']),
    ('short_nap', 'sleep', 'Подремни кратко следобед, ако имаш нужда.',
     'Кратката дрямка освежава, без да пречи на нощта.', 'timer', 'minutes', {'1': 20}, 1, 20,
     [], {}, []),
    # --- social -------------------------------------------------------------
    ('coffee_with_friend', 'social', 'Пий кафе или чай с някого.',
     'Споделеното време радва.', 'confirm', '', {}, 2, 30, [], {}, ['call_friend']),
    ('reconnect_old_friend', 'social', 'Свържи се със стар приятел.',
     'Възстановените връзки топлят.', 'confirm', '', {}, 2, 10, [], {}, ['write_message']),
    ('compliment_someone', 'social', 'Направи искрен комплимент.',
     'Добрата дума радва двама.', 'confirm', '', {}, 1, 1, [], {}, []),
    ('family_call', 'social', 'Обади се на член от семейството.',
     'Семейството е опора.', 'confirm', '', {}, 1, 10, [], {}, ['call_friend']),
    ('neighbor_chat', 'social', 'Размени няколко думи със съсед.',
     'Малките разговори намаляват самотата.', 'confirm', '', {}, 1, 5, [], {}, []),
    ('volunteer', 'social', 'Помогни доброволно на кауза.',
     'Даването свързва с общността.', 'confirm', '', {}, 3, 60, [], {}, ['help_someone']),
    ('group_activity', 'social', 'Присъедини се към обща дейност.',
     'Заедно е по-леко и по-весело.', 'confirm', '', {}, 2, 45, [], {}, ['coffee_with_friend']),
    ('send_photo', 'social', 'Изпрати снимка на близък човек.',
     'Споделените моменти сближават.', 'confirm', '', {}, 1, 2, [], {}, ['write_message']),
    # --- mind ---------------------------------------------------------------
    ('mindful_tea', 'mind', 'Изпий чай, без да бързаш.',
     'Спокойният ритуал успокоява ума.', 'timer', 'minutes', {'1': 5}, 1, 5, [], {},
     ['breathing']),
    ('sunlight_moment', 'mind', 'Постой на дневна светлина.',
     'Светлината повдига настроението.', 'confirm', '', {}, 1, 10, [],
     {'rain': 'sit_by_window'}, ['nature_moment']),
    ('declutter_spot', 'mind', 'Подреди едно малко кътче.',
     'Редът навън успокоява отвътре.', 'confirm', '', {}, 1, 10, [], {}, []),
    ('puzzle_game', 'mind', 'Реши кръстословица или пъзел.',
     'Игрите пазят ума остър.', 'timer', 'minutes', {'1': 10}, 1, 15, [], {},
     ['learn_something']),
    ('write_letter', 'mind', 'Напиши писмо или бележка на ръка.',
     'Писането на ръка успокоява.', 'confirm', '', {}, 2, 15, [], {}, ['journal']),
    ('hobby_time', 'mind', 'Отдели време за любимо занимание.',
     'Хобитата зареждат с радост.', 'confirm', '', {}, 1, 20, [], {}, []),
    ('slow_walk_mindful', 'mind', 'Разходи се бавно и осъзнато.',
     'Осъзнатата разходка успокоява ума.', 'location', 'minutes', {'1': 10}, 1, 10,
     ['severe_joint_pain'], {'rain': 'march_indoors'}, ['breathing']),
    ('affirm_positive', 'mind', 'Кажи си едно окуражаващо изречение.',
     'Добрите думи към себе си помагат.', 'confirm', '', {}, 1, 1, [], {}, []),
    ('observe_five', 'mind', 'Забележи 5 неща около теб.',
     'Вниманието към момента намалява тревогата.', 'confirm', '', {}, 1, 3, [], {},
     ['breathing']),
    # --- financial ----------------------------------------------------------
    ('weekly_budget', 'financial', 'Планирай разходите за седмицата.',
     'Планът носи спокойствие.', 'confirm', '', {}, 2, 15, [], {}, ['track_expense']),
    ('compare_prices', 'financial', 'Сравни цени преди покупка.',
     'Малкото сравнение спестява.', 'confirm', '', {}, 1, 5, [], {}, []),
    ('cook_instead_out', 'financial', 'Сготви вкъщи вместо да поръчаш навън.',
     'Домашното е по-евтино и по-здравословно.', 'confirm', '', {}, 2, 30, [], {},
     ['home_cooked']),
    ('cancel_unused', 'financial', 'Откажи услуга, която не ползваш.',
     'Спестяваш, без да губиш нищо.', 'confirm', '', {}, 2, 10, [], {},
     ['review_subscription']),
    ('save_change', 'financial', 'Прибери рестото в касичка.',
     'Дребните монети се събират.', 'confirm', '', {}, 1, 2, [], {}, ['small_saving']),
    ('list_before_shop', 'financial', 'Направи списък преди пазаруване.',
     'Списъкът пази от излишни покупки.', 'confirm', '', {}, 1, 5, [], {}, ['no_spend_day']),
    ('energy_saving', 'financial', 'Изгаси уредите, които не ползваш.',
     'По-малка сметка, по-чиста съвест.', 'confirm', '', {}, 1, 2, [], {}, []),
]

# Retro-tag a couple of existing high-intensity actions now that the tags exist.
UPDATES = {
    'stairs_walk':      ['severe_joint_pain', 'cardiac', 'balance_issues', 'respiratory'],
    'balance_practice': ['acute_injury', 'balance_issues'],
}


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
    for slug, contra in UPDATES.items():
        ActionDef.objects.filter(slug=slug).update(contraindications=contra)


def unseed(apps, schema_editor):
    ActionDef = apps.get_model('plans', 'ActionDef')
    ActionDef.objects.filter(slug__in=[a[0] for a in ACTIONS]).delete()
    # restore prior contraindications for the retro-tagged actions
    ActionDef.objects.filter(slug='stairs_walk').update(contraindications=['severe_joint_pain'])
    ActionDef.objects.filter(slug='balance_practice').update(contraindications=['acute_injury'])


class Migration(migrations.Migration):
    dependencies = [('plans', '0011_expand_action_library')]
    operations = [migrations.RunPython(seed, unseed)]
