from django.test import TestCase,Client
from django.urls import reverse
from .models import *
import json
# Create your tests here.

class TestViews(TestCase):

    def setUp(self):
       
        self.loginurl=reverse("login")
        self.validateurl=reverse("validate")
        self.profileurl=reverse("profile")
        self.client=Client()


    def test_otp(self):
        response=self.client.get(self.profileurl,Authorization="Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6IjIwMjIwMDAwMDAwMDciLCJleHAiOjE2NDc4Nzc0MTMuMzc0MDExfQ.VF0F58NjwAdeilJUMmIEr0NTTCgK5eXli6wq4rFVBF4")

        self.assertEquals(response.status_code,200)
