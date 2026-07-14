# 1Step

MVP уеб приложение, което помага на хора над 50 години да получат персонален 7-дневен стартов план за по-здрав, активен и балансиран живот.

## Инсталация

### 1. Клониране / разархивиране на проекта

```bash
cd moiat_plan_50
```

### 2. Създаване и активиране на виртуална среда

```bash
python3 -m venv venv
source venv/bin/activate        # Mac/Linux
# или: venv\Scripts\activate   # Windows
```

### 3. Инсталиране на зависимости

```bash
pip install -r requirements.txt
```

> **Забележка за WeasyPrint:** Ако имате проблеми с инсталацията на WeasyPrint,
> вижте: https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#installation
>
> На macOS: `brew install pango libffi`
>
> Ако изберете да пропуснете WeasyPrint, всичко работи освен PDF export.

### 4. Стартиране на миграции

```bash
python manage.py migrate
```

### 5. Създаване на superuser (за Django Admin)

```bash
python manage.py createsuperuser
```

Въведете username, email (по желание) и парола.

### 6. Стартиране на сървъра

```bash
python manage.py runserver
```

Отворете браузъра на: **http://127.0.0.1:8000**

## Тестване на приложението

### Потребителски поток:

1. Отидете на http://127.0.0.1:8000
2. Натиснете **„Започни моя план"**
3. Попълнете въпросника (всички задължителни полета)
4. Вижте резултата – профил и 7-дневен план
5. Натиснете **„Изтегли PDF"** (изисква WeasyPrint)
6. Натиснете **„Остави обратна връзка"** и попълнете формата

### Django Admin:

Отидете на http://127.0.0.1:8000/admin и влезте с createsuperuser данните.

Там можете да прегледате:
- **Отговори от въпросник** – всички попълнени въпросници
- **Лични планове** – генерираните планове
- **Обратни връзки** – feedback от потребителите

## Структура на проекта

```
moiat_plan_50/
├── manage.py
├── requirements.txt
├── README.md
├── onestep/               # Django project package (was moiat_plan_50/)
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── plans/
    ├── models.py          # QuestionnaireResponse, UserPlan, Feedback
    ├── forms.py           # Django forms с BG labels и choices
    ├── views.py           # home, questionnaire, result, download_pdf, feedback
    ├── urls.py            # URL конфигурация
    ├── admin.py           # Django admin регистрации
    ├── profile_logic.py   # determine_profile() и generate_plan()
    ├── migrations/
    └── templates/plans/
        ├── base.html
        ├── home.html
        ├── questionnaire.html
        ├── result.html
        ├── feedback.html
        ├── feedback_success.html
        └── pdf_plan.html
```

## Профили

| Профил | Условие |
|--------|---------|
| Лек старт | movement_level == 'ниско' И energy_level <= 2 |
| Отслабване без стрес | main_goal == 'отслабване' |
| Повече енергия | main_goal == 'енергия' |
| Социално активиране | social_activity == 'ниска' |
| Баланс и поддръжка | всички останали случаи |

## Disclaimer

Приложението предоставя **общи препоръки за активен и балансиран начин на живот**.
Не е медицинска консултация. При здравословни проблеми се консултирайте с лекар.
