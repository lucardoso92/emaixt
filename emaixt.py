import re
import argparse
import sys
import requests
from lxml import html
from multiprocessing.pool import Pool


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
                timeout=5,
                verify=False
            )

            if response.status_code == 200:
                return response.text
        except Exception:
            pass

    def _get_emails(self, page: str) -> list:
        page_lxml = html.fromstring(page)
        emails = list()

        # search @mailto
        mailtos = page_lxml.xpath('//*[contains(@href, "mailto")]/@href')
        emails += [self._clean_mail(x) for x in mailtos]

        # search @regex
        # regex = r'(?:[a-z0-9!#$%&\'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&\'*+/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9]))\.){3}(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9])|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])'
        regex = r'^[a-zA-Z0-9-_]+@[a-zA-Z0-9]+\.[a-z]{1,3}$'
        emails_regex = re.finditer(regex, page)
        emails += [self._clean_mail(x.group(0)) for x in emails_regex]

        return list(dict.fromkeys(emails))

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
        '-u',
        '--url',
        help="URL to enumerate emails",
        required=True
    )

    parser.add_argument(
        '-s',
        '--silent',
        help='Enable the silent mode',
        action=argparse.BooleanOptionalAction
    )
    parser.set_defaults(silent=False)
    parser.set_defaults(pipe=False)

    return parser.parse_args()


def test_pipe():
    try:
        return sys.argv[1] == 'pipe'
    except Exception:
        return False


def execute(url: str, silent: bool = True) -> None:
    emxt = Emaixt(website=url, silent=silent)
    emxt.main()


def interactive():
    pipe = test_pipe()

    if not pipe:
        args = parse_args()
        url = args.url
        silent = args.silent
        baner(silent=silent)
        execute(url, silent)

        if not silent:
            print()
    else:
        sites = [line.strip() for line in sys.stdin]
        pool = Pool(processes=5)
        pool.map(execute, sites)


if __name__ == '__main__':
    interactive()
