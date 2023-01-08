from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from http import HTTPStatus

User = get_user_model()


class UserUrlTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        cls.user = User.objects.create_user(username='Pol')

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(UserUrlTest.user)

    def test_chek_url(self):
        res_logout = self.authorized_client.get('/auth/logout/')
        res_login = self.guest_client.get('/auth/login/')
        res_signup = self.guest_client.get('/auth/signup/')
        test_dict = {
            res_logout: HTTPStatus.OK,
            res_login: HTTPStatus.OK,
            res_signup: HTTPStatus.OK
        }
        for response, expected_value in test_dict.items():
            with self.subTest(response=response):
                self.assertEqual(
                    response.status_code, expected_value, 'oops!')

    def test_check_templates(self):
        test_dict = {
            '/auth/logout/': 'users/logged_out.html',
            '/auth/login/': 'users/login.html',
            '/auth/signup/': 'users/signup.html'
        }
        for adress, template in test_dict.items():
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                self.assertTemplateUsed(response, template)
