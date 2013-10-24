from bottle import response

from unittest import TestCase
from mock import Mock, patch
from mock import call
from bottle_registration import SimpleRegFlow, ActivateAccountRegFlow, login_required


class BaseRegFlowTest(TestCase):
    USERNAME = "John"
    EMAIL = "John@Doe.com"
    PWD = "Doeh!"
    PWD2 = "Duh!"
    FIRSTNAME = "JohnnyBoy"
    AGE = 22

    def test_register_good_username_pwd(self):
        backend = self.get_simple_reg_backend()

        result = backend.register(self.USERNAME, self.PWD)

        self.assertTrue(backend.auth_db.store_user.called)
        self.assertTrue(backend.auth_db.store_user.call_args,
            call(self.USERNAME, self.PWD))

    def test_register_takes_additional_arguments(self):
        backend = self.get_simple_reg_backend()

        result = backend.register(self.USERNAME, self.PWD,
            firstname=self.FIRSTNAME, age=self.AGE)

        self.assertEqual(backend.auth_db.store_user.call_args[1],
            {'age': self.AGE, 'firstname': self.FIRSTNAME})

    def test_random_session_id_returns_id_as_string(self):
        backend = self.get_simple_reg_backend()

        session_id = backend.random_session_id

        self.assertEqual(len(session_id), 32)
        self.assertEqual(type(session_id), str)

    def get_simple_reg_backend(self):
        return SimpleRegFlow(auth_db=Mock())


class AccountActivationBaseRegFlowTest(TestCase):
    USERNAME = "John"
    EMAIL = "John@Doe.com"
    PWD = "Doeh!"
    PWD2 = "Duh!"
    FIRSTNAME = "JohnnyBoy"
    AGE = 22

    def test_register_does_send_email(self):
        backend = self.get_simple_reg_backend()
        backend.send_account_activation_mail = Mock()

        result = backend.register(username=self.USERNAME, pwd=self.PWD,
            firstname=self.FIRSTNAME, age=self.AGE, email=self.EMAIL)

        self.assertEqual(backend.auth_db.store_user.call_args[1],
            {'age': self.AGE, 'firstname': self.FIRSTNAME,
             'email': self.EMAIL})

        self.assertTrue(backend.send_account_activation_mail.called)

    def get_simple_reg_backend(self):
        return ActivateAccountRegFlow(auth_db=Mock())


class LoginRequiredTest(TestCase):

    @patch('bottle_registration.redirect')
    def test_custom_login_required_url(self, bottle_redirect):
        reg_flow = Mock(login_required_url='/test-login')
        view = Mock()

        result = login_required(view)(reg_flow=reg_flow)

        self.assertTrue(bottle_redirect.called)
        self.assertTrue(bottle_redirect.call_args == call('/test-login'))

    @patch('bottle_registration.redirect')
    def test_when_a_user_is_not_logged_in_redirect(self, bottle_redirect):
        reg_flow = Mock()
        view = Mock()

        result = login_required(view)(reg_flow=reg_flow)

        self.assertTrue(bottle_redirect.called)