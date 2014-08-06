from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.test import TestCase
from cards.forms import EmailUserCreationForm
from cards.models import Card, Player
from cards.test_utils import run_pyflakes_for_package, run_pep8_for_package
from cards.utils import create_deck


class BasicMathTestCase(TestCase):
    def test_math(self):
        a = 1
        b = 1
        self.assertEqual(a + b, 2)

    # def test_failing_case(self):
    #     a = 1
    #     b = 1
    #     self.assertEqual(a+b, 1)


class UtilTestCase(TestCase):
    def test_create_deck_count(self):
        """TEST THAT WE CREATED 52 CARDS"""
        create_deck()
        self.assertEqual(Card.objects.count(), 52)


class ModelTestCase(TestCase):
    def test_get_ranking(self):
        """Test that we get the proper ranking for a card"""
        card = Card.objects.create(suit=Card.CLUB, rank="jack")
        self.assertEqual(card.get_ranking(), 11)

    def test_get_war_result_tie(self):
        """War logic equal cards"""
        five = Card.objects.create(suit=Card.CLUB, rank="five")
        five2 = Card.objects.create(suit=Card.HEART, rank="five")
        self.assertEqual(five.get_war_result(five2), 0)

    def test_get_war_result_loss(self):
        six = Card.objects.create(suit=Card.SPADE, rank="six")
        four = Card.objects.create(suit=Card.SPADE, rank='four')
        self.assertEqual(four.get_war_result(six), -1)

    def test_get_war_result_win(self):
        six = Card.objects.create(suit=Card.SPADE, rank="six")
        four = Card.objects.create(suit=Card.SPADE, rank='four')
        self.assertEqual(six.get_war_result(four), 1)


class FormTestCase(TestCase):
    def test_clean_username_error(self):
        # Create a player so that this username we're testing is already taken
        Player.objects.create_user(username='test-user')

        # set up the form for testing
        form = EmailUserCreationForm()
        form.cleaned_data = {'username': 'test-user'}

        # use a context manager to watch for the validation error being raised
        with self.assertRaises(ValidationError):
            form.clean_username()

    def test_clean_username_username(self):
        form = EmailUserCreationForm()
        form.cleaned_data = {'username': 'test2-user'}
        self.assertEqual(form.clean_username(), 'test2-user')


class ViewTestCase(TestCase):
    def setUp(self):
        create_deck()

    def test_home_page(self):
        response = self.client.get(reverse('home'))
        self.assertIn('<p>Suit: spade, Rank: two</p>', response.content)
        self.assertEqual(response.context['cards'].count(), 52)

    def test_faq_page(self):
        response = self.client.get(reverse('faq'))
        self.assertIn('<p>Q: Can I win real money on this website?</p>', response.content)

    def test_filters_page(self):
        response = self.client.get(reverse('filter'))
        self.assertIn('<p>Capitalized Suit: 2</p>', response.content)
        self.assertEqual(response.context['cards'].count(), 52)

    # def test_login_page(self):
    #     password = 'password'
    #     user = Player.objects.create_user(username = "test-user", email="test@test.com", )


class SyntaxTest(TestCase):
    def test_syntax(self):
        """
        Run pyflakes/pep8 across the code base to check for potential errors.
        """
        packages = ['cards']
        warnings = []
        # Eventually should use flake8 instead so we can ignore specific lines via a comment
        for package in packages:
            warnings.extend(run_pyflakes_for_package(package, extra_ignore=("_settings",)))
            warnings.extend(run_pep8_for_package(package, extra_ignore=("_settings",)))
        if warnings:
            self.fail("{0} Syntax warnings!\n\n{1}".format(len(warnings), "\n".join(warnings)))
