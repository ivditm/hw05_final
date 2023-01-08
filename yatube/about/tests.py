from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from http import HTTPStatus

User = get_user_model()


class AboutURLTests(TestCase):

    def setUp(self):
        self.guest_client = Client()

    def test_check_url(self):
        res_author = self.guest_client.get('/about/author/')
        res_tech = self.guest_client.get('/about/tech/')
        test_dict = {
            res_author: HTTPStatus.OK,
            res_tech: HTTPStatus.OK
        }
        for response, expected_value in test_dict.items():
            with self.subTest(response=response):
                self.assertEqual(
                    response.status_code, expected_value, 'oops!'
                )

    def test_check_template(self):
        test_dict = {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html'
        }
        for adress, template in test_dict.items():
            with self.subTest(adress=adress):
                response = self.guest_client.get(adress)
                self.assertTemplateUsed(response, template)

    def test_check_name(self):
        test_dict = {
            reverse('about:author'): 'about/author.html',
            reverse('about:tech'): 'about/tech.html'
        }
        for reverse_name, template in test_dict.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
