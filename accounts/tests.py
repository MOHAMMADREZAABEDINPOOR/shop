from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User, Address

class AccountsSecurityAndFlowTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(
            email="user1@shop.local",
            password="SecurePass1234!",
            first_name="User",
            last_name="One",
            role=User.Role.CUSTOMER
        )
        self.user2 = User.objects.create_user(
            email="user2@shop.local",
            password="SecurePass1234!",
            first_name="User",
            last_name="Two",
            role=User.Role.CUSTOMER
        )
        self.addr1 = Address.objects.create(
            user=self.user1,
            title="User 1 Address",
            receiver_name="User One",
            receiver_phone="09120000001",
            province="Tehran",
            city="Tehran",
            postal_code="1234567890",
            address_line="Street 1"
        )

    def test_user_registration_flow(self):
        res = self.client.post(reverse('accounts:register'), {
            'email': 'newcustomer@shop.local',
            'phone_number': '09129998877',
            'first_name': 'New',
            'last_name': 'Customer',
            'password': 'StrongPassword123!',
            'password_confirm': 'StrongPassword123!'
        })
        self.assertEqual(res.status_code, 302)
        new_user = User.objects.filter(email='newcustomer@shop.local').first()
        self.assertIsNotNone(new_user)
        self.assertTrue(new_user.check_password('StrongPassword123!'))

    def test_user_login_and_logout(self):
        res = self.client.post(reverse('accounts:login'), {
            'email': 'user1@shop.local',
            'password': 'SecurePass1234!'
        })
        self.assertEqual(res.status_code, 302)
        self.assertIn('_auth_user_id', self.client.session)

        # Logout
        res_logout = self.client.get(reverse('accounts:logout'))
        self.assertEqual(res_logout.status_code, 302)
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_address_idor_protection(self):
        """User 2 must NOT be able to edit or delete User 1's address."""
        self.client.login(username='user2@shop.local', password='SecurePass1234!')

        # Attempt to edit user1's address
        res_edit = self.client.get(reverse('accounts:address_edit', kwargs={'pk': self.addr1.pk}))
        self.assertEqual(res_edit.status_code, 404)

        # Attempt to delete user1's address
        res_delete = self.client.post(reverse('accounts:address_delete', kwargs={'pk': self.addr1.pk}))
        self.assertEqual(res_delete.status_code, 404)
        self.assertTrue(Address.objects.filter(pk=self.addr1.pk).exists())
