from api.models import Project
from rest_framework import status
from rest_framework.test import APITestCase
import json
import requests


class AccountTests(APITestCase):
    def test_create_account(self):
        """
        Ensure we can create a new account object.
        """
        url = 'http://127.0.0.1:8000/api/projects/'
        data = {
            "name": "titan",
            "packages": [
                {
                    "name": "Django",
                    "version": "1.0.4"
                },
                {
                    "name": "graphene",
                    "version": "2.0"
                },
                {
                    "name": "numpy",
                    "version": "0.9.6"
                },
                {
                    "name": "tornado",
                    "version": "0.2"
                }
            ]
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Project.objects.count(), 1)
        self.assertEqual(Project.objects.get().name, 'titan')
        response = self.client.get(url, format='json')
        data1 = {
            "name": "titan2",
            "packages": [
                {
                    "name": "Django",
                    "version": "1.0.4"
                },
                {
                    "name": "graphene",
                    "version": "2.0"
                },
                {
                    "name": "numpy",
                    "version": "0.9.6"
                },
                {
                    "name": "tornado",
                    "version": "0.2"
                }
            ]
        }
        self.assertDictEqual(response.json()[0], data)
        response = self.client.patch(url+"titan", {'packages':
                                                   [{"name": "Django",
                                                     "version": "1.0.2"}]},
                                     format='json')
        self.assertEqual(Project.objects.count(), 1)
        response = self.client.get('http://127.0.0.1:8000/api/projects/titan')
        print(response.content)
