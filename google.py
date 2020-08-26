import json
import os
import re

import requests

from bypass_botguard import ByPassGoogleBotGuard

# Forked from: https://github.com/Aruelius/Google_login


class Google(object):
    def __init__(self, identifier, username=""):
        """
        identifier is very very important!!!
        identifier is very very important!!!
        identifier is very very important!!!
        The important thing should say three times.
        """
        self.bypass_botguard = ByPassGoogleBotGuard()
        self.identifier = identifier
        self.username = username
        self.session = requests.session()
        self.session.headers.update(
            {
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36"
            }
        )
        self.sms_url = (
            lambda sms_tl: f"https://accounts.google.com/_/signin/selectchallenge?hl=en&TL={sms_tl}"
        )
        self.challenge_url = (
            lambda TL: f"https://accounts.google.com/_/signin/challenge?hl=en&TL={TL}"
        )
        self.SERVICE = "youtube"
        self.YOUTUBE_URL = "https://www.youtube.com"
        self.LOOKUP_URL = "https://accounts.google.com/_/lookup/accountlookup?hl=en-CA"
        self.SERVICE_LOGIN_URL = "https://accounts.google.com/ServiceLogin"
        self.CONTINUE_URL = "https://www.youtube.com/signin?action_handle_signin=true&app=desktop&hl=en-CA&next=https%3A%2F%2Fwww.youtube.com%2F"

    def req(self, url: str, f_req: list, xsrf: str, bghash=None):
        data = {
            "continue": self.CONTINUE_URL,
            "service": self.SERVICE,
            "hl": "en-CA",
            "f.req": json.dumps(f_req),
            "bgRequest": json.dumps(["identifier", self.bypass_botguard.generate_bg_request_data()]),
            # 'at': xsrf,
            "azt": xsrf,
            "deviceinfo": json.dumps(
                [
                    None,
                    None,
                    None,
                    [],
                    None,
                    "US",
                    None,
                    None,
                    [],
                    "GlifWebSignIn",
                    None,
                    [
                        None,
                        None,
                        [],
                        None,
                        None,
                        None,
                        None,
                        None,
                        None,
                        None,
                        None,
                        None,
                        None,
                        None,
                        None,
                        None,
                        None,
                        None,
                        None,
                        None,
                        None,
                        None,
                        None,
                        None,
                        None,
                        [],
                        None,
                        None,
                        None,
                        [],
                        [],
                    ],
                    None,
                    None,
                    None,
                    None,
                    2,
                ]
            ),
        }
        if bghash:
            data["bghash"] = bghash
        r = self.session.post(url=url, data=data)
        response = json.loads(r.text.replace(")]}'", ""))
        return response

    def service_login(self):
        r = self.session.get(
            url=self.SERVICE_LOGIN_URL,
            params={
                "service": self.SERVICE,
                "continue": self.CONTINUE_URL,
                "hl": "en-CA",
            },
        ).text
        xsrf = (
            re.findall(r"window.WIZ_global_data = (.+?);", r)[0]
            .split('"')[10]
            .replace("\\", "")
        )
        config_list = (
            re.findall(r'data-initial-setup-data="%(.*?);]', r, re.S)[0]
            .replace("&quot", '"')
            .split('";')
        )
        bghash = config_list[-1][:-2]
        user_hash = config_list[3]
        self.session.headers.update(
            {
                "google-accounts-xsrf": "1",
                "content-type": "application/x-www-form-urlencoded;charset=UTF-8",
            }
        )
        return xsrf, bghash, user_hash

    def account_lookup(self, username):
        lookup_username = username or self.username
        if not lookup_username:
            return None
        xsrf, bghash, user_hash = self.service_login()
        lookup_req = [
            lookup_username,
            user_hash,
            [],
            None,
            "US",
            None,
            None,
            2,
            False,
            True,
            [
                None,
                None,
                [
                    2,
                    1,
                    None,
                    1,
                    "https://accounts.google.com/ServiceLogin?service=youtube&uilel=3&passive=True&continue=https%3A%2F%2Fwww.youtube.com%2Fsignin%3Faction_handle_signin%3DTrue%26app%3Ddesktop%26hl%3Den-CA%26next%3Dhttps%253A%252F%252Fwww.youtube.com%252F&hl=en-CA&ec=65620",
                    None,
                    [],
                    4,
                    [],
                    "GlifWebSignIn",
                    None,
                    [],
                ],
                1,
                [
                    None,
                    None,
                    [],
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    [],
                    None,
                    None,
                    None,
                    [],
                    [],
                ],
                None,
                None,
                None,
                True,
            ],
            lookup_username,
            None,
            None,
            None,
            True,
            True,
            [],
        ]
        response = self.req(self.LOOKUP_URL, lookup_req, xsrf)
        print(self.identifier)
        print(lookup_username)
        print(response)
        try:
            response[1][-1]
        except IndexError:
            print("identifier invalid")
            os._exit(0)
        return lookup_username in str(response)
