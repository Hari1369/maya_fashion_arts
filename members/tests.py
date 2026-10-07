from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class UserManagementTests(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser(
            username="owner",
            email="owner@example.com",
            password="TestPass9284!Secure",
        )
        self.staff = User.objects.create_user(
            username="manager",
            password="TestPass9284!Secure",
            is_staff=True,
        )
        self.member = User.objects.create_user(
            username="member",
            password="TestPass9284!Secure",
            email="member@example.com",
        )

    def test_user_details_requires_superuser(self):
        for url in (
            reverse("members:user_detail"),
            reverse("members:userdetails"),
        ):
            self.assertEqual(self.client.get(url).status_code, 302)

        self.client.force_login(self.staff)
        for url in (
            reverse("members:user_detail"),
            reverse("members:userdetails"),
        ):
            self.assertEqual(self.client.get(url).status_code, 403)

    def test_registration_is_available_to_anyone(self):
        response = self.client.get(reverse("members:register"))
        self.assertEqual(response.status_code, 200)

        self.client.force_login(self.member)
        response = self.client.get(reverse("members:register"))
        self.assertEqual(response.status_code, 200)

    def test_superuser_can_open_user_details(self):
        self.client.force_login(self.superuser)

        details = self.client.get(reverse("members:userdetails"))

        self.assertEqual(details.status_code, 200)
        self.assertEqual(details.request["PATH_INFO"], "/userdetails/")
        self.assertContains(details, "member@example.com")
        self.assertContains(details, "Update")
        self.assertContains(details, "Delete")

    def test_user_details_named_alias_opens_user_details(self):
        self.client.force_login(self.superuser)

        response = self.client.get(reverse("members:user_detail"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request["PATH_INFO"], "/userdetails/")

    def test_anyone_can_register_a_regular_user(self):
        response = self.client.post(
            reverse("members:register"),
            {
                "username": "newmember",
                "first_name": "New",
                "last_name": "Member",
                "email": "newmember@example.com",
                "password1": "BlueSkyPass9284!",
                "password2": "BlueSkyPass9284!",
            },
        )

        self.assertRedirects(response, reverse("core:dashboard"))
        user = User.objects.get(username="newmember")
        self.assertEqual(user.email, "newmember@example.com")
        self.assertTrue(user.check_password("BlueSkyPass9284!"))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_superuser_can_update_inline_user_details(self):
        self.client.force_login(self.superuser)

        response = self.client.post(
            reverse("members:userdetails"),
            {
                "action": "update",
                "user_id": self.member.pk,
                "username": self.member.username,
                "first_name": "Updated",
                "last_name": "Name",
                "email": "updated@example.com",
                "is_staff": "on",
                "is_superuser": "on",
            },
        )

        self.assertRedirects(response, reverse("members:userdetails"))
        self.member.refresh_from_db()
        self.assertEqual(self.member.first_name, "Updated")
        self.assertEqual(self.member.email, "updated@example.com")
        self.assertFalse(self.member.is_staff)
        self.assertFalse(self.member.is_superuser)

    def test_superuser_can_delete_with_post(self):
        self.client.force_login(self.superuser)

        response = self.client.post(
            reverse("members:userdetails"),
            {"action": "delete", "user_id": self.member.pk},
        )

        self.assertRedirects(response, reverse("members:userdetails"))
        self.assertFalse(User.objects.filter(pk=self.member.pk).exists())

    def test_superuser_cannot_delete_their_own_account(self):
        self.client.force_login(self.superuser)

        response = self.client.post(
            reverse("members:userdetails"),
            {"action": "delete", "user_id": self.superuser.pk},
        )

        self.assertRedirects(response, reverse("members:userdetails"))
        self.assertTrue(User.objects.filter(pk=self.superuser.pk).exists())
