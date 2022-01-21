from django.test import TestCase,Client,LiveServerTestCase
from django.urls import reverse
from .models import *

import requests

# Create your tests here.

class UserLoginTest(LiveServerTestCase):


    def test_login(self):
        res=requests.post(self.live_server_url+reverse("login"),data={
                "number":"9791026856"
                    })
        res_json=res.json()
        self.assertEqual(res.status_code,200)
        self.assertEqual(res_json["ERR"],None)
        self.assertEqual(res_json["MSG"],"SUCCESS")

        body=res_json["BODY"]

        res=requests.post(self.live_server_url+reverse("validate"),data=body)
         
        res_json=res.json()

        self.assertEqual(res.status_code,200)
        self.assertEqual(res_json["ERR"],None)

        self.assertEqual(res_json["MSG"],"SUCCESS")

        token=res_json["BODY"]["token"]

        res=requests.get(self.live_server_url+reverse("profile"),headers={
                "Authorization":"Bearer "+token
                })

        res_json=res.json()
        
        self.assertEqual(res.status_code,200)

