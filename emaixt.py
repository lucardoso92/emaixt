import argparse
import sys
import requests
from lxml import html


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
        headers = {
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
        }
        response = requests.get(url=self.website, headers=headers)

        if response.status_code == 200:
            return response.text

        raise 'site not working'

    def _get_emails(self, page: str) -> list:
        page_lxml = html.fromstring(page)
        emails = list()

        # search @mailto
        mailtos = page_lxml.xpath('//*[contains(@href, "mailto")]/@href')
        emails += [self._clean_mail(x) for x in mailtos]

        return emails

    def main(self) -> None:
        page = self._get_page()
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

    return parser.parse_args()


def interactive():
    args = parse_args()
    url = args.url
    silent = args.silent

    baner(silent=silent)

    emxt = Emaixt(website=url, silent=silent)
    emxt.main()


if __name__ == '__main__':
    interactive()
