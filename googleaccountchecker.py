from pathlib import Path
from datetime import datetime
from http.cookiejar import MozillaCookieJar
from requests import Session
import requests
from http import cookiejar
import re
import hashlib


class GoogleAccountChecker:
    __cookies: MozillaCookieJar
    __session: Session = requests.Session()
    __epoch_time: int = int(datetime.now().timestamp())
    __docs_url: str

    def __init__(self, cookies_path: Path):
        self.__set_cookies(cookies_path)

    def __set_cookies(self, path: Path):
        self.__cookies = cookiejar.MozillaCookieJar(path)
        self.__cookies.load(ignore_discard=True, ignore_expires=True)
        for cookie in self.__cookies:
            self.__session.cookies.set_cookie(cookie)

    def __generate_sapisid(self) -> str:
        sapisid = next(
            cookie for cookie in self.__cookies if cookie.name == "SAPISID"
        ).value
        sapisid_hash = hashlib.sha1()
        sapisid_str = f"{self.__epoch_time} {sapisid} https://docs.google.com"
        sapisid_hash.update(bytes(sapisid_str, "utf-8"))
        return f"{self.__epoch_time}_{sapisid_hash.hexdigest()}"

    def __set_headers(self, sapisid_hash: str, api_key: str):
        self.__session.headers.update(
            {
                "authority": "people-pa.clients6.google.com",
                "x-user-agent": "grpc-web-javascript/0.1",
                "accept-language": "en-US,en;q=0.9",
                "authorization": f"SAPISIDHASH {sapisid_hash}",
                "content-type": "application/json+protobuf",
                "accept": "*/*",
                "x-goog-api-key": api_key,
                "x-goog-authuser": "0",
                "origin": "https://docs.google.com",
                "sec-fetch-site": "same-site",
                "sec-fetch-mode": "cors",
                "sec-fetch-dest": "empty",
                "referer": self.__docs_url,
            }
        )

    def check(self, email: str) -> bool:
        data = [
            [email],
            2,
            None,
            None,
            [None, None, None, ["DRIVE_SHARE", None, 2]],
            [
                [
                    [
                        "person.name",
                        "person.photo",
                        "person.email",
                        "person.metadata",
                        "person.name.metadata.verified",
                        "person.email.metadata.verified",
                    ]
                ],
                None,
                [2, 8, 1, 7, 10, 11],
                None,
                None,
                [],
            ],
            [],
            [None, None, [], None, None, [1], [[1]], None, [3]],
            [[23, 36]],
            [],
        ]
        resp = self.__session.post(
            "https://people-pa.clients6.google.com/$rpc/google.internal.people.v2.minimal.InternalPeopleMinimalService/ListPeopleByKnownId",
            json=data,
        ).json()
        return len(resp) > 0 and resp[0][0][0] == email

    def setup(self, docs_id: str):
        self.__docs_url = f"https://docs.google.com/sharing/driveshare?id={docs_id}&foreignService=kix&gaiaService=writely&shareService=kix&command=init_share&subapp=10&popupWindowsEnabled=true&shareUiType=default&hl=en&authuser=0&rand={self.__epoch_time}&locationHint=unknown&preload=false"
        page_source = self.__session.get(self.__docs_url,)
        sapisid_hash = self.__generate_sapisid()
        api_key = re.search(r'v2internal\\",\\"(.+?)\\', page_source.text).group(1)
        self.__set_headers(sapisid_hash, api_key)
