from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from django.test import TestCase
from users.views import UserViewset
from users.models import CustomUser

class ViewTestCase(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.url = reverse('users-list')
        data = {'email': 'user@user.com', 'password': 'foo'}
        self.response = self.client.post(self.url, data, format='json')

    def test_api_can_create_a_user(self):
        self.assertEqual(self.response.status_code, status.HTTP_201_CREATED)

    def test_api_can_get_a_user(self):
        user = CustomUser.objects.get()
        response = self.client.get(reverse('users-detail', kwargs={'pk': user.id}), format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, user)

    def test_api_can_update_a_user(self):
        user = CustomUser.objects.get()
        change_user = {'email': 'user2@user.com', 'password': 'moo'}
        response = self.client.put(reverse('users-detail', kwargs={'pk': user.id}), change_user, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_api_can_delete_a_user(self):
        user = CustomUser.objects.get()
        response = self.client.delete(reverse('users-detail', kwargs={'pk': user.id}), format='json', follow=True)
        self.assertEquals(response.status_code, status.HTTP_204_NO_CONTENT)