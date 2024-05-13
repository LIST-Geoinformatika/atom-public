from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from user.models import Organization, User


class UserApiTestCase(APITestCase):

    def setUp(self):

        self.organization = Organization.objects.create(name="test organization")

        self.user01 = User.objects.create(
            username="user01",
            email="test@example.com",
            first_name="User",
            last_name="01",
            organization=self.organization
        )
        self.user01.set_password('test1234')

        self.user02 = User.objects.create(
            username="user02",
            email="test02@example.com",
            first_name="User",
            last_name="02",
            organization=self.organization
        )

    def test_user_delete_forbidden(self):
        self.client.force_authenticate(self.user02)
        url = reverse("user_delete", kwargs={"pk": self.user01.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_delete_success(self):
        self.client.force_authenticate(self.user01)
        url = reverse("user_delete", kwargs={"pk": self.user01.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_user_password_change_bad_request(self):
        self.client.force_authenticate(self.user01)
        url = reverse("change_password")
        data = {'old_password': 'wrong-paasword', 'new_password': 'pass1234'}
        response = self.client.put(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_password_change_too_comon(self):
        self.client.force_authenticate(self.user01)
        url = reverse("change_password")
        data = {'old_password': 'test1234', 'new_password': 'pass1234'}
        response = self.client.put(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_password_change_success(self):
        self.client.force_authenticate(self.user01)
        url = reverse("change_password")
        data = {'old_password': 'test1234', 'new_password': 'listlabs12'}
        response = self.client.put(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
