from datetime import datetime
import json
from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from reservations.models import ParkingSpot, Reservation, WaitlistEntry

class LoginTest(TestCase):

    def setUp(self):
        self.username = 'testkorisnik'
        self.password = 'tajnalozinka123'
        self.user = User.objects.create_user(username=self.username, password=self.password)

    def test_logout(self):
        response = self.client.post(
            reverse('logout_user')
        )

        self.assertRedirects(response, '/')

        response = self.client.get('/')

        self.assertEqual(response.status_code, 200)

    def test_login_success(self):
        response = self.client.post(
            reverse('login_user'), 
            {'username': self.username, 'password': self.password}
        )

        self.assertRedirects(response, '/main')

        response = self.client.get('/main')
        self.assertEqual(response.status_code, 200)

    def test_login_failure(self):
        response = self.client.post(
            reverse('login_user'),
            {'username': self.username, 'password': 'pogresna_lozinka'}
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Please enter a correct username and password") 

    def test_login_nonexistent_user(self):
        response = self.client.post(
            reverse('login_user'),
            {'username': 'nepostojeci', 'password': 'bilošta'}
        )

        self.assertEqual(response.status_code, 200)

        self.assertContains(response, "Please enter a correct username and password")


class RegisterTest(TestCase):
    def setUp(self):
        self.register_url = reverse('register_user')
        self.existing_user = User.objects.create_user(username='testkorisnik', password='tajna123')

    def test_successful_registration(self):
        response = self.client.post(self.register_url, {
            'username': 'novikorisnik',
            'email': 'novi@email.com',
            'password1': 'dobraLozinka123',
            'password2': 'dobraLozinka123',
        })

        self.assertTrue(User.objects.filter(username='novikorisnik').exists())

        self.assertRedirects(response, '/main')

    def test_registration_existing_user(self):
        response = self.client.post(self.register_url, {
            'username': 'testkorisnik', 
            'email': 'drugi@email.com',
            'password1': 'nekaLozinka123',
            'password2': 'nekaLozinka123',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "A user with that username already exists.")

    def test_registration_short_password(self):
        response = self.client.post(self.register_url, {
            'username': 'noviuser',
            'email': 'email@email.com',
            'password1': '123',
            'password2': '123',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This password is too short.")

    def test_registration_passwords_dont_match(self):
        response = self.client.post(self.register_url, {
            'username': 'noviuser2',
            'email': 'email2@email.com',
            'password1': 'lozinka123',
            'password2': 'drugalozinka321',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "The two password fields didn’t match.")


class MainPageTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.spot = ParkingSpot.objects.create(number=1)

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('main_page'))
        self.assertEqual(response.status_code, 302)

    def test_main_page_logged_in(self):
        self.client.login(username="testuser", password="testpass")
        response = self.client.get(reverse('main_page'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main.html')


class ReserveSpotTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.spot = ParkingSpot.objects.create(number=1)
        self.client.login(username="testuser", password="testpass")

    def test_reserve_spot_successfully(self):
        response = self.client.post(
            reverse('reserve'),
            json.dumps({'spot_id': self.spot.id, 'date': datetime.today().strftime('%Y-%m-%d')}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])

    def test_duplicate_reservation_same_user(self):
        Reservation.objects.create(user=self.user, spot=self.spot, date=datetime.today())
        response = self.client.post(
            reverse('reserve'),
            json.dumps({'spot_id': self.spot.id, 'date': datetime.today().strftime('%Y-%m-%d')}),
            content_type='application/json'
        )
        self.assertFalse(response.json()['success'])


class UnreserveSpotTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="testpass", email="test@example.com")
        self.spot = ParkingSpot.objects.create(number=1)
        self.date = datetime.today().date()
        self.client.login(username="testuser", password="testpass")
        Reservation.objects.create(user=self.user, spot=self.spot, date=self.date)

    def test_unreserve_own_spot(self):
        response = self.client.post(
            reverse('unreserve'),
            json.dumps({'spot_id': self.spot.id, 'date': self.date.strftime('%Y-%m-%d')}),
            content_type='application/json'
        )
        self.assertTrue(response.json()['success'])

    def test_unreserve_not_your_spot(self):
        other_user = User.objects.create_user(username="other", password="pass")
        Reservation.objects.all().delete()
        Reservation.objects.create(user=other_user, spot=self.spot, date=self.date)
        response = self.client.post(
            reverse('unreserve'),
            json.dumps({'spot_id': self.spot.id, 'date': self.date.strftime('%Y-%m-%d')}),
            content_type='application/json'
        )
        self.assertFalse(response.json()['success'])


class InterestQueueTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.client.login(username="testuser", password="testpass")

    def test_join_waitlist_success(self):
        response = self.client.post(reverse('interest_queue'), data={"date": "2025-05-20"})
        self.assertRedirects(response, '/main')
        self.assertTrue(WaitlistEntry.objects.filter(user=self.user, date="2025-05-20").exists())

    def test_join_waitlist_invalid_date(self):
        response = self.client.post(reverse('interest_queue'), data={"date": "not-a-date"})
        self.assertRedirects(response, '/main')
