# Bloom — ITC4214 Final Project

A Django-based volunteer platform with a merch shop and donation system.

## Setup

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## User Credentials

| Username | Password   | Role       |
|----------|------------|------------|
| admin    | admin1234  | Superuser  |
| testuser | user1234   | Regular    |
| emilios  | emilios1234| Regular    |

## Key URLs

| Page            | URL                  |
|-----------------|----------------------|
| Homepage        | /                    |
| Tasks           | /tasks/              |
| Impact          | /impact/             |
| About           | /about/              |
| Contact         | /contact/            |
| Support/Shop    | /shop/support/       |
| Cart            | /shop/cart/          |
| Dashboard       | /accounts/dashboard/ |
| Profile         | /accounts/profile/   |
| Admin Panel     | /panel/              |

## Notes

- Set `DEBUG = False` and configure `ALLOWED_HOSTS` before deployment
- Run `python manage.py collectstatic` before deployment
- $1 donation = 5 trees planted
