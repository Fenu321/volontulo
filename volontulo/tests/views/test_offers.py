# -*- coding: utf-8 -*-

u"""
.. module:: test_offers
"""

from django.contrib.auth.models import User
from django.test import Client
from django.test import TestCase

from volontulo.models import Offer
from volontulo.models import Organization
from volontulo.models import UserProfile


class TestOffersList(TestCase):
    u"""Class responsible for testing offers' list."""

    @classmethod
    def setUpTestData(cls):
        u"""Set up data for all tests."""
        organization = Organization.objects.create(
            name=u'',
            address=u'',
            description=u'',
        )
        organization.save()

        common_offer_data = {
            'organization': organization,
            'description': u'',
            'requirements': u'',
            'time_commitment': u'',
            'benefits': u'',
            'location': u'',
            'title': u'volontulo offer',
            'time_period': u''
        }

        cls.inactive_offer = Offer.objects.create(
            status='NEW',
            **common_offer_data
        )
        cls.inactive_offer.save()
        cls.active_offer = Offer.objects.create(
            status='ACTIVE',
            **common_offer_data
        )
        cls.active_offer.save()

        volunteer_user = User.objects.create_user(
            u'volunteer@example.com',
            u'volunteer@example.com',
            u'123volunteer'
        )
        volunteer_user.save()
        cls.volunteer = UserProfile(user=volunteer_user)
        cls.volunteer.save()

        organization_user = User.objects.create_user(
            u'organization@example.com',
            u'organization@example.com',
            u'123org'
        )
        organization_user.save()
        cls.organization = UserProfile(
            user=organization_user,
        )
        cls.organization.save()
        # pylint: disable=no-member
        cls.organization.organizations.add(organization)

        admin_user = User.objects.create_user(
            u'admin@example.com',
            u'admin@example.com',
            u'123admin'
        )
        admin_user.save()
        cls.admin = UserProfile(
            user=admin_user,
            is_administrator=True,
        )
        cls.admin.save()

    def setUp(self):
        u"""Set up each test."""
        self.client = Client()

    # pylint: disable=invalid-name
    def _test_offers_list_for_standard_user(self):
        u"""Test offers' list for standard user.

        List of offers is available for standard users and shows only ACTIVE
        offers.
        Test are common for anonymous user, volunteer and organization.
        """
        response = self.client.get('/offers')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'offers/offers_list.html')
        # pylint: disable=no-member
        self.assertIn('offers', response.context)
        # pylint: disable=no-member
        self.assertEqual(len(response.context['offers']), 1)
        # pylint: disable=no-member
        self.assertEqual(response.context['offers'][0].status, 'ACTIVE')

    def test_offer_list_for_anonymous_user(self):
        u"""Test offers' list for anonymus user."""
        return self._test_offers_list_for_standard_user()

    def test_offers_list_for_volunteer(self):
        u"""Test offers' list for account of volunteer."""
        self.client.post('/login', {
            'email': u'volunteer@example.com',
            'password': '123volunteer',
        })
        return self._test_offers_list_for_standard_user()

    def test_offers_list_for_organization(self):
        u"""Test offers' list for account of organization."""
        self.client.post('/login', {
            'email': u'organization@example.com',
            'password': '123org',
        })
        return self._test_offers_list_for_standard_user()

    def test_offers_list_for_admin(self):
        u"""Test offers' list for account of admin."""
        self.client.post('/login', {
            'email': u'admin@example.com',
            'password': '123admin',
        })
        response = self.client.get('/offers')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'offers/offers_list.html')
        # pylint: disable=no-member
        self.assertIn('offers', response.context)
        # pylint: disable=no-member
        self.assertEqual(len(response.context['offers']), 2)


class TestOffersCreate(TestCase):
    u"""Class responsible for testing offer's create page."""

    @classmethod
    def setUpTestData(cls):
        u"""Set up data for all tests."""
        organization = Organization.objects.create(
            name=u'',
            address=u'',
            description=u'',
        )
        organization.save()
        organization_user = User.objects.create_user(
            u'organization@example.com',
            u'organization@example.com',
            u'123org'
        )
        organization_user.save()
        cls.organization_profile = UserProfile(
            user=organization_user,
        )
        cls.organization_profile.save()
        # pylint: disable=no-member
        cls.organization_profile.organizations.add(organization)

    def setUp(self):
        u"""Set up each test."""
        self.client = Client()

    def test_offers_create_get_method(self):
        u"""Test page for offer creation - tendering template with form."""
        self.client.post('/login', {
            'email': u'organization@example.com',
            'password': '123org',
        })
        response = self.client.get('/offers/create')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'offers/offer_form.html')

    def test_offers_create_invalid_form(self):
        u"""Test attempt of creation of new offer with invalid form."""
        self.client.post('/login', {
            'email': u'organization@example.com',
            'password': '123org',
        })
        response = self.client.post('/offers/create', {})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'offers/offer_form.html')
        self.assertContains(
            response,
            u'Formularz zawiera niepoprawnie wypełnione pola'
        )

    def test_offers_create_valid_form(self):
        u"""Test attempt of creation of new offer with valid form."""
        self.client.post('/login', {
            'email': u'organization@example.com',
            'password': '123org',
        })
        for i in range(1, 11):
            response = self.client.post('/offers/create', {
                'organization': u'1',
                'description': u'required description',
                'requirements': u'required requirements',
                'time_commitment': u'required time_commitment',
                'benefits': u'required benefits',
                'location': u'required location',
                'title': u'volontulo offer',
                'time_period': u'required time_period',
            }, follow=True)
            self.assertRedirects(
                response,
                '/offers/volontulo-offer/{}'.format(i),
                302,
                200,
            )
            offer = Offer.objects.get(id=i)
            self.assertEqual(
                offer.organization,
                self.organization_profile.organizations.all()[0],
            )
            self.assertEqual(offer.description, u'required description')
            self.assertEqual(offer.requirements, u'required requirements')
            self.assertEqual(
                offer.time_commitment,
                u'required time_commitment'
            )
            self.assertEqual(offer.benefits, u'required benefits')
            self.assertEqual(offer.location, u'required location')
            self.assertEqual(offer.title, u'volontulo offer')
            self.assertEqual(offer.time_period, u'required time_period')


class TestOffersEdit(TestCase):
    u"""Class responsible for testing offer's edit page."""

    @classmethod
    def setUpTestData(cls):
        u"""Set up data for all tests."""
        organization = Organization.objects.create(
            name=u'',
            address=u'',
            description=u'',
        )
        organization.save()
        organization_user = User.objects.create_user(
            u'organization@example.com',
            u'organization@example.com',
            u'123org'
        )
        organization_user.save()
        cls.organization_profile = UserProfile(
            user=organization_user,
        )
        cls.organization_profile.save()
        # pylint: disable=no-member
        cls.organization_profile.organizations.add(organization)
        cls.offer = Offer.objects.create(
            organization=organization,
            description=u'',
            requirements=u'',
            time_commitment=u'',
            benefits=u'',
            location=u'',
            title=u'volontulo offer',
            time_period=u'',
            status='NEW',
        )
        cls.offer.save()

    def setUp(self):
        u"""Set up each test."""
        self.client = Client()

    def test_for_non_existing_offer(self):
        u"""Test if error 404 will be raised when offer dosn't exits."""
        self.client.post('/login', {
            'email': u'organization@example.com',
            'password': '123org',
        })
        response = self.client.get('/offers/some-slug/42/edit')
        self.assertEqual(response.status_code, 404)

    def test_for_different_slug(self):
        u"""Test if redirect will be raised when offer has different slug."""
        self.client.post('/login', {
            'email': u'organization@example.com',
            'password': '123org',
        })
        response = self.client.get('/offers/different-slug/1/edit')
        self.assertRedirects(
            response,
            '/offers/volontulo-offer/1/edit',
            302,
            200,
        )

    def test_for_correct_slug(self):
        u"""Test of get request for offers/edit with correct slug."""
        self.client.post('/login', {
            'email': u'organization@example.com',
            'password': '123org',
        })
        response = self.client.get('/offers/volontulo-offer/1/edit')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'offers/offer_form.html')

    def test_offers_edit_invalid_form(self):
        u"""Test attempt of edition of offer with invalid form."""
        self.client.post('/login', {
            'email': u'organization@example.com',
            'password': '123org',
        })
        response = self.client.post('/offers/volontulo-offer/1/edit', {
            'edit_type': 'full_edit',
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'offers/offer_form.html')
        self.assertContains(
            response,
            u'Formularz zawiera niepoprawnie wypełnione pola'
        )
        offer = Offer.objects.get(id=1)
        self.assertEqual(
            offer.organization,
            self.organization_profile.organizations.all()[0],
        )
        self.assertEqual(offer.description, u'')
        self.assertEqual(offer.requirements, u'')
        self.assertEqual(
            offer.time_commitment,
            u''
        )
        self.assertEqual(offer.benefits, u'')
        self.assertEqual(offer.location, u'')
        self.assertEqual(offer.title, u'volontulo offer')
        self.assertEqual(offer.time_period, u'')

    def test_offers_edit_valid_form(self):
        u"""Test attempt of edition of offer with valid form."""
        self.client.post('/login', {
            'email': u'organization@example.com',
            'password': '123org',
        })
        response = self.client.post('/offers/volontulo-offer/1/edit', {
            'edit_type': 'full_edit',
            'organization': u'1',
            'description': u'required description',
            'requirements': u'required requirements',
            'time_commitment': u'required time_commitment',
            'benefits': u'required benefits',
            'location': u'required location',
            'title': u'another volontulo offer',
            'time_period': u'required time_period',
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'offers/offer_form.html')
        self.assertContains(
            response,
            u'Oferta została zmieniona.'
        )
        offer = Offer.objects.get(id=1)
        self.assertEqual(
            offer.organization,
            self.organization_profile.organizations.all()[0],
        )
        self.assertEqual(offer.description, u'required description')
        self.assertEqual(offer.requirements, u'required requirements')
        self.assertEqual(
            offer.time_commitment,
            u'required time_commitment'
        )
        self.assertEqual(offer.benefits, u'required benefits')
        self.assertEqual(offer.location, u'required location')
        self.assertEqual(offer.title, u'another volontulo offer')
        self.assertEqual(offer.time_period, u'required time_period')

    def test_offers_status_change(self):
        u"""Test status change made using offers/edit."""
        self.client.post('/login', {
            'email': u'organization@example.com',
            'password': '123org',
        })
        response = self.client.post('/offers/volontulo-offer/1/edit', {
            'edit_type': 'status_change',
            'status': 'ACTIVE'
        })
        self.assertRedirects(
            response,
            '/offers',
            302,
            200,
        )
        offer = Offer.objects.get(id=1)
        self.assertEqual(offer.status, u'ACTIVE')