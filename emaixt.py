import re
import argparse
import sys
import urllib3
from multiprocessing.pool import Pool
from requests_html import HTMLSession
from requests import Session
from functools import partial
from lxml import html
from email_validator import validate_email, EmailNotValidError
from fake_useragent import UserAgent


urllib3.disable_warnings()


class Emaixt:
    def __init__(self, website: str, silent: bool = False, js_render: bool = False) -> None:
        self.website = website
        self.silent = silent
        self.js_render = js_render

    def _clean_mail(self, mail: str) -> str:
        mail = mail.strip()
        mail = mail.replace('mailto', '')
        mail = mail.replace(':', '')
        mail = mail.strip()
        return mail

    def _get_page(self):
        try:
            session = Session() if not self.js_render else HTMLSession()
            ua = UserAgent()
            headers = {
                "User-Agent": ua.random,
            }
            response = session.get(
                url=self.website,
                headers=headers,
                timeout=10,
                verify=False
            )
            if self.js_render:
                response.html.render()
                response_text = response.html.raw_html.decode()
            else:
                response_text = response.text
            if response.status_code == 200:
                return response_text
        except Exception as e:
            print('[error] -', e)
            pass

    def _validate_email(self, email):
        try:
            validation = validate_email(email)

            email = validation.email
            return email

        except EmailNotValidError:
            return ''

    def _get_emails(self, page: str) -> list:
        try:
            page_lxml = html.fromstring(page)
            emails = list()

            # search @mailto
            mailtos = page_lxml.xpath('//*[contains(@href, "mailto")]/@href')
            emails += [self._clean_mail(x) for x in mailtos]

            # search @regex
            regex = r'''(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9]))\.){3}(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9])|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])'''
            emails_regex = re.finditer(regex, page)
            emails += [self._clean_mail(x.group(0)) for x in emails_regex]

            # Validate email
            emails = [self._validate_email(x) for x in emails]
            emails = [x for x in emails if x != '']

            return list(dict.fromkeys(emails))

        except ValueError:
            return []

    def main(self) -> None:
        page = self._get_page()
        if page:
            emails = self._get_emails(page=page)
            for email in emails:
                print(email)


def baner(silent: bool) -> None:
    title = '''
███████╗███╗   ███╗ █████╗ ██╗██╗  ██╗████████╗
██╔════╝████╗ ████║██╔══██╗██║╚██╗██╔╝╚══██╔══╝
█████╗  ██╔████╔██║███████║██║ ╚███╔╝    ██║   
██╔══╝  ██║╚██╔╝██║██╔══██║██║ ██╔██╗    ██║   
███████╗██║ ╚═╝ ██║██║  ██║██║██╔╝ ██╗   ██║   
╚══════╝╚═╝     ╚═╝╚═╝  ╚═╝╚═╝╚═╝  ╚═╝   ╚═╝   
                                             
Author: Lucas Cardoso
'''
    if not silent:
        print(title)


def parse_args() -> argparse.ArgumentParser:
    # parse the arguments
    parser = argparse.ArgumentParser(
        epilog='\tExample: \r\npython ' +
        sys.argv[0] + " -u https://www.example.com/contact"
    )

    parser._optionals.title = "OPTIONS"

    parser.add_argument(
        '-s',
        '--silent',
        help='Enable the silent mode',
        action=argparse.BooleanOptionalAction
    )

    parser.add_argument(
        '-p',
        '--pipe',
        help='Enable the pipe mode',
        action=argparse.BooleanOptionalAction
    )

    parser.add_argument(
        '-js',
        '--js_render',
        help='Enable the js render mode (slow mode)',
        action=argparse.BooleanOptionalAction
    )

    parser.add_argument(
        '-u',
        '--url',
        help="URL to enumerate emails",
        required='--pipe' not in sys.argv
    )

    parser.set_defaults(silent=False)
    parser.set_defaults(pipe=False)
    parser.set_defaults(js_render=False)

    final_parser = parser.parse_args()

    return final_parser


def execute(silent: bool, js_render: bool, url: str) -> None:
    emxt = Emaixt(website=url, silent=silent, js_render=js_render)
    emxt.main()


def interactive() -> None:
    args = parse_args()
    silent = args.silent
    js_render = args.js_render

    baner(silent=silent)

    if not args.pipe:
        url = args.url
        execute(silent, js_render, url)
    else:
        sites = [line.strip() for line in sys.stdin]
        func = partial(execute, silent, js_render)
        pool = Pool(processes=5)
        pool.map(func, sites)

    if not silent:
        print()


if __name__ == '__main__':
    interactive()
