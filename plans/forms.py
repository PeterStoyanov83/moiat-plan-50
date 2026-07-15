from django import forms
from .models import QuestionnaireResponse, Feedback

GENDER_CHOICES = [
    ('мъж', 'Мъж'),
    ('жена', 'Жена'),
    ('друго', 'Предпочитам да не посочвам'),
]

WORKING_STATUS_CHOICES = [
    ('работещ', 'Работещ'),
    ('пенсионер', 'Пенсионер'),
    ('частично_работещ', 'Работя на непълно работно време'),
    ('безработен', 'Безработен / Свободна практика'),
]

LIVING_STATUS_CHOICES = [
    ('сам', 'Сам/а'),
    ('с_партньор', 'С партньор'),
    ('със_семейство', 'Със семейство'),
    ('с_деца', 'С деца / внуци'),
]

ENERGY_CHOICES = [(i, str(i)) for i in range(1, 6)]

SLEEP_CHOICES = [
    (5, 'По-малко от 6 часа'),
    (6, '6 часа'),
    (7, '7 часа'),
    (8, '8 часа'),
    (9, '9 или повече часа'),
]

EATING_FREQUENCY_CHOICES = [
    ('1_2', '1-2 пъти дневно'),
    ('3', '3 пъти дневно'),
    ('4_5', '4-5 пъти дневно (с междинни)'),
    ('безредно', 'Нередовно / пропускам закуска'),
]

EVENING_MEAL_CHOICES = [
    ('лека', 'Лека вечеря (зеленчуци, супа)'),
    ('средна', 'Средна порция'),
    ('обилна', 'Обилна вечеря'),
    ('късно', 'Вечерям след 20:00'),
]

MAIN_GOAL_CHOICES = [
    ('отслабване', 'Искам да отслабна'),
    ('енергия', 'Искам повече енергия'),
    ('движение', 'Искам да се движа повече'),
    ('социалност', 'Искам повече социален живот'),
    ('баланс', 'Искам баланс и добра форма'),
]

MOVEMENT_LEVEL_CHOICES = [
    ('ниско', 'Почти не се движа'),
    ('леко', 'Леко – разходки понякога'),
    ('умерено', 'Умерено – 2-3 пъти седмично'),
    ('активно', 'Активно – всеки ден'),
]

PREFERRED_MOVEMENT_CHOICES = [
    ('ходене', 'Ходене пеш'),
    ('колело', 'Колело'),
    ('плуване', 'Плуване'),
    ('гимнастика', 'Лека гимнастика у дома'),
    ('йога', 'Йога / стречинг'),
    ('групови', 'Групови занимания'),
    ('друго', 'Друго'),
]

JOINT_PAIN_CHOICES = [
    ('не', 'Не'),
    ('леко', 'Леко – не ми пречи'),
    ('умерено', 'Умерено – ограничава ме понякога'),
    ('силно', 'Силно – пречи ми да се движа'),
]

SOCIAL_ACTIVITY_CHOICES = [
    ('ниска', 'Рядко се виждам с хора'),
    ('средна', 'Понякога се срещам с приятели/семейство'),
    ('висока', 'Редовно имам социални контакти'),
    ('много_висока', 'Имам богат социален живот'),
]

SCORE_CHOICES = [(i, str(i)) for i in range(1, 6)]

PRICE_CHOICES = [
    ('', 'Не мога да преценя'),
    ('безплатно', 'Само безплатно'),
    ('1_5', '1-5 лв.'),
    ('5_10', '5-10 лв.'),
    ('10_20', '10-20 лв.'),
    ('20+', 'Повече от 20 лв.'),
]


class QuestionnaireForm(forms.ModelForm):
    first_name = forms.CharField(
        label='Как да се обръщаме към вас?',
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'напр. Петър'}),
    )
    age = forms.IntegerField(
        label='Колко години сте?',
        min_value=40, max_value=100,
        widget=forms.NumberInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'напр. 57'}),
    )
    gender = forms.ChoiceField(
        label='Пол',
        choices=GENDER_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
    )
    height = forms.IntegerField(
        label='Ръст (в см)',
        min_value=140, max_value=220,
        widget=forms.NumberInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'напр. 168'}),
    )
    weight = forms.IntegerField(
        label='Тегло (в кг)',
        min_value=40, max_value=250,
        widget=forms.NumberInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'напр. 82'}),
    )
    working_status = forms.ChoiceField(
        label='Какъв е вашият работен статус?',
        choices=WORKING_STATUS_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
    )
    living_status = forms.ChoiceField(
        label='С кого живеете?',
        choices=LIVING_STATUS_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
    )
    energy_level = forms.ChoiceField(
        label='Как бихте оценили нивото си на енергия? (1 = много ниско, 5 = отлично)',
        choices=ENERGY_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
    )
    sleep_hours = forms.ChoiceField(
        label='Колко часа спите средно на нощ?',
        choices=SLEEP_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
    )
    health_limitations = forms.CharField(
        label='Имате ли здравословни ограничения, за които трябва да се съобразяваме?',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'напр. болки в коляното, диабет тип 2 (по желание)',
        }),
    )
    eating_frequency = forms.ChoiceField(
        label='Колко пъти на ден се храните?',
        choices=EATING_FREQUENCY_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
    )
    evening_meal_type = forms.ChoiceField(
        label='Как обикновено изглежда вечерята ви?',
        choices=EVENING_MEAL_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
    )
    main_goal = forms.ChoiceField(
        label='Коя е вашата основна цел?',
        choices=MAIN_GOAL_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
    )
    movement_level = forms.ChoiceField(
        label='Как бихте описали сегашното си ниво на физическа активност?',
        choices=MOVEMENT_LEVEL_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
    )
    preferred_movement = forms.MultipleChoiceField(
        label='Какъв вид движение предпочитате? (може да изберете повече от едно)',
        choices=PREFERRED_MOVEMENT_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
    )
    joint_pain = forms.ChoiceField(
        label='Имате ли болки в ставите или гръбначния стълб?',
        choices=JOINT_PAIN_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
    )
    social_activity = forms.ChoiceField(
        label='Как бихте описали социалната си активност?',
        choices=SOCIAL_ACTIVITY_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
    )
    has_hobby = forms.BooleanField(
        label='Имате ли хоби или занимание, което ви доставя удоволствие?',
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    )
    ninety_day_goal = forms.CharField(
        label='Какво искате да постигнете за 90 дни? (напишете с ваши думи)',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'напр. "Искам да се чувствам по-леко и да имам енергия за внуците"',
        }),
    )
    consent_given = forms.BooleanField(
        label='Съгласявам се личните ми данни (включително здравна информация) да бъдат '
              'обработени за изготвяне на моя личен план.',
        required=True,
        error_messages={'required': 'Трябва да се съгласите, за да продължите.'},
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    )

    class Meta:
        model = QuestionnaireResponse
        fields = [
            'first_name',
            'age', 'gender', 'height', 'weight', 'working_status', 'living_status',
            'energy_level', 'sleep_hours', 'health_limitations', 'eating_frequency',
            'evening_meal_type', 'main_goal', 'movement_level', 'preferred_movement',
            'joint_pain', 'social_activity', 'has_hobby', 'ninety_day_goal',
            'consent_given',
        ]

    def clean_energy_level(self):
        return int(self.cleaned_data['energy_level'])

    def clean_sleep_hours(self):
        return int(self.cleaned_data['sleep_hours'])

    def clean_preferred_movement(self):
        return ', '.join(self.cleaned_data['preferred_movement'])


class FeedbackForm(forms.ModelForm):
    clarity_score = forms.ChoiceField(
        label='Колко ясен беше планът? (1 = неясен, 5 = много ясен)',
        choices=SCORE_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
    )
    usefulness_score = forms.ChoiceField(
        label='Колко полезен беше планът за вас? (1 = изобщо не, 5 = много полезен)',
        choices=SCORE_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
    )
    realistic_score = forms.ChoiceField(
        label='Колко реалистичен е планът? (1 = нереалистичен, 5 = напълно реалистичен)',
        choices=SCORE_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
    )
    would_use_again = forms.BooleanField(
        label='Бихте ли използвали отново тази услуга?',
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    )
    would_pay = forms.BooleanField(
        label='Бихте ли платили за персонализиран план?',
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    )
    suggested_price = forms.ChoiceField(
        label='Колко бихте платили?',
        choices=PRICE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select form-select-lg'}),
    )
    most_useful_part = forms.CharField(
        label='Кое беше най-полезното за вас?',
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
    )
    improvement_suggestion = forms.CharField(
        label='Какво бихте подобрили?',
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
    )

    class Meta:
        model = Feedback
        fields = [
            'clarity_score', 'usefulness_score', 'realistic_score',
            'would_use_again', 'would_pay', 'suggested_price',
            'most_useful_part', 'improvement_suggestion',
        ]

    def clean_clarity_score(self):
        return int(self.cleaned_data['clarity_score'])

    def clean_usefulness_score(self):
        return int(self.cleaned_data['usefulness_score'])

    def clean_realistic_score(self):
        return int(self.cleaned_data['realistic_score'])
