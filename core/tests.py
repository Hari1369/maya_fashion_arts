from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class DashboardTests(TestCase):
    def test_dashboard_is_available_to_everyone(self):
        response = self.client.get(reverse("core:dashboard"))
        self.assertEqual(response.status_code, 200)

        user = User.objects.create_user(username="member", password="test-password")
        self.client.force_login(user)
        response = self.client.get(reverse("core:dashboard"))
        self.assertEqual(response.status_code, 200)

    def test_dashboard_is_available_to_superuser(self):
        user = User.objects.create_superuser(
            username="owner",
            email="owner@example.com",
            password="test-password",
        )
        self.client.force_login(user)

        response = self.client.get(reverse("core:dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Dashboard")
        self.assertContains(response, 'id="sidebar-toggle"')
        self.assertContains(response, 'id="app-sidebar"')

    def test_user_details_link_is_only_shown_to_superusers(self):
        anonymous_response = self.client.get(reverse("core:dashboard"))
        self.assertNotContains(anonymous_response, "User details")

        user = User.objects.create_user(username="member", password="test-password")
        self.client.force_login(user)
        member_response = self.client.get(reverse("core:dashboard"))
        self.assertNotContains(member_response, "User details")

        admin = User.objects.create_superuser(
            username="owner",
            email="owner@example.com",
            password="test-password",
        )
        self.client.force_login(admin)
        admin_response = self.client.get(reverse("core:dashboard"))
        self.assertContains(admin_response, "User details")
