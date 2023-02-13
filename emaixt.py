import re
import argparse
import sys
import urllib3
import requests
from functools import partial
from lxml import html
from multiprocessing.pool import Pool

urllib3.disable_warnings()


class Emaixt:
    def __init__(self, website: str, silent: bool = False) -> None:
        self.website = website
        self.silent = silent

    def _clean_mail(self, mail: str) -> str:
        mail = mail.strip()
        mail = mail.replace('mailto', '')
        mail = mail.replace(':', '')
        mail = mail.strip()
        return mail

    def _get_page(self):
        try:
            headers = {
                'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
            }
            response = requests.get(
                url=self.website,
                headers=headers,
                timeout=10,
                verify=False
            )

            if response.status_code == 200:
                return response.text
        except Exception:
            pass

    def _get_emails(self, page: str) -> list:
        try:
            page_lxml = html.fromstring(page)
            emails = list()

            # search @mailto
            mailtos = page_lxml.xpath('//*[contains(@href, "mailto")]/@href')
            emails += [self._clean_mail(x) for x in mailtos]

            # search @regex
            regex = r'[a-zA-Z0-9.!#$%&’*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)'
            emails_regex = re.finditer(regex, page)
            emails += [self._clean_mail(x.group(0)) for x in emails_regex]

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
:::::::::: ::::    ::::      :::     ::::::::::: :::    ::: ::::::::::: 
:+:        +:+:+: :+:+:+   :+: :+:       :+:     :+:    :+:     :+:     
+:+        +:+ +:+:+ +:+  +:+   +:+      +:+      +:+  +:+      +:+     
+#++:++#   +#+  +:+  +#+ +#++:++#++:     +#+       +#++:+       +#+     
+#+        +#+       +#+ +#+     +#+     +#+      +#+  +#+      +#+     
#+#        #+#       #+# #+#     #+#     #+#     #+#    #+#     #+#     
########## ###       ### ###     ### ########### ###    ###     ###     

createdBy: Lucas Cardoso
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
        '-u',
        '--url',
        help="URL to enumerate emails",
        required='--pipe' not in sys.argv
    )

    parser.set_defaults(silent=False)
    parser.set_defaults(pipe=False)

    final_parser = parser.parse_args()

    return final_parser


def execute(silent: bool, url: str) -> None:
    emxt = Emaixt(website=url, silent=silent)
    emxt.main()


def interactive() -> None:
    args = parse_args()
    silent = args.silent

    baner(silent=silent)

    if not args.pipe:
        url = args.url
        execute(url, silent)
    else:
        sites = [line.strip() for line in sys.stdin]
        func = partial(execute, silent)
        pool = Pool(processes=5)
        pool.map(func, sites)

    if not silent:
        print()


if __name__ == '__main__':
    interactive()
