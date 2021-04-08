from typing import Dict, Union
from django.test import TestCase
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from api.decorators import check_response
from django.utils.decorators import method_decorator


User = get_user_model()

USER_CREDENTIALS: Dict[str, str] = {
   "username": "newUser",
   "password": "myPasswordWith."
}

UPDATED_CREDENTIALS: Dict[str, Union[str, int]] = {
    'first_name': 'changedName',
    'gender': 'Male',
    'phone': 8456217463
}


class ProfileTestCase(TestCase):
    def __init__(self, *args, **kwargs):
        super(ProfileTestCase, self).__init__(*args, **kwargs)
        self.failureException = ValueError
        self.longMessage = False

    def setUp(self) -> None:
        """
            Setup the test user, and log in with the test user to access the profile page
        """
        self.user = User.objects.create_user(**USER_CREDENTIALS)
        self.client.login(**USER_CREDENTIALS)

    @method_decorator(check_response(path="/api/v1/user/"))
    def test_get_user(self):
        res: JsonResponse = self.client.get("/api/v1/user/")
        self.assertEqual(self.user.username, res.json()['username'])

        self.client.logout()
        res: JsonResponse = self.client.get("/api/v1/user/")
        self.assertEqual('anonymous', res.json()['username'])
        self.client.login(**USER_CREDENTIALS)

    @method_decorator(check_response(path="/api/v1/profile/"))
    def test_get_output(self):
        """
            Tests if the GET requests to profile are working and also returning the correct response
        """
        self.res = self.client.get('/api/v1/profile/')
        self.assert_('first_name' in self.res.json(), 'First name is not returned')
        self.assert_('last_name' in self.res.json(), 'Last name is not returned')
        self.assert_('phone' in self.res.json(), 'Phone number is not returned')
        self.assert_('gender' in self.res.json(), 'Gender is not returned')
        self.assert_('is_seller' in self.res.json(), 'Seller details are not returned')
        is_seller = self.res.json()['is_seller']
        self.assertIsInstance(is_seller, bool)

    @method_decorator(check_response(path="/api/v1/profile/", method="POST", post_data={}))
    def test_post_output(self):
        """
        Tests if the POST requests to profile are working and also returning the correct response
        """
        self.client.login(**USER_CREDENTIALS)
        __res: JsonResponse = self.client.get('/api/v1/profile/')
        _data: dict = __res.json()
        _data.update(UPDATED_CREDENTIALS)

        res: JsonResponse = self.client.post('/api/v1/profile/', _data)

        self.assertEqual(res.status_code, 200)

        # Check if data has been modified
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, UPDATED_CREDENTIALS['first_name'])
        self.assertEqual(self.user.userprofile.gender, UPDATED_CREDENTIALS['gender'])
        self.assertEqual(self.user.userprofile.phone, UPDATED_CREDENTIALS['phone'])


class TestLoginLogout(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(**USER_CREDENTIALS)
        # self.client.login(**USER_CREDENTIALS)

    @method_decorator(check_response(path="/api/v1/login/"))
    def test_login(self):
        res = self.client.post('/api/v1/login/', USER_CREDENTIALS)
        self.assertEqual(res.status_code, 200)       # Check the correct code

        res = self.client.get('/api/v1/user/')
        self.assertEqual(res.json()['loggedIn'], True, "User hasn't been logged out")

    def test_logout(self):
        # Currently the user is logged out
        res = self.client.post('/api/v1/logout/')
        self.assertEqual(res.status_code, 400, 'Not able to handle invalid logout request')

        self.client.login(**USER_CREDENTIALS)
        res = self.client.post('/api/v1/logout/')
        self.assertEqual(res.status_code, 200, 'User is not able to logout')

        res = self.client.get('/api/v1/user/')
        self.assertEqual(res.json()['loggedIn'], False, "User hasn't been logged out")
