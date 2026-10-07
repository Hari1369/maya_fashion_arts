# maya_fashion_arts

## User accounts

The site uses Django's built-in `auth.User` model and `auth_user` table.
The dashboard at `/` is open to everyone. Anyone can register at `/register/`.
The user-details table at `/userdetails/` is restricted to signed-in
superusers. These custom pages are separate from the Django admin screen.

The user-details page lists users and provides inline update and delete actions.
Passwords and permission fields are not exposed in the update form. Deletion
uses a POST confirmation and superusers cannot delete their own account.

To initialize a development database and create a staff administrator, run:

```sh
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

The custom pages use Bootstrap 5 styling from its public CDN.