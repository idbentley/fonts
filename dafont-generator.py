import argparse
import requests
import hashlib
import os

pkgbuild_template = """
pkgname={pkgname}
pkgver=1
pkgrel=1
pkgdesc=""
arch=(any)
license=('')
url='{url}'
depends=('fontconfig' 'xorg-font-utils')
source=('{dl_url}')
install=$pkgname.install
md5sums=('{md5}')


package() {{
  mkdir -p "${{pkgdir}}/usr/share/fonts/TTF/"
  install -m644 "${{srcdir}}/"*.ttf "${{pkgdir}}/usr/share/fonts/TTF/"
}}
"""

install_template = """
post_install() {
  fc-cache -s
}

post_upgrade() {
  post_install
}

post_remove() {
  post_install
}
"""

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--url", required=True)

    args = parser.parse_args()

    pkgname = args.url[len("http://www.dafont.com/"):-len(".font")]

    dl_url = "http://dl.dafont.com/dl/?f={}".format(pkgname.replace("-", "_"))

    headers = {
        'Host': "dl.dafont.com",
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36',
        'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        'Accept-Language': "en-US,en;q=0.5",
        'Accept-Encoding': "gzip, deflate",
        'Referer': args.url,
        'Connection': "keep-alive",
        'Upgrade-Insecure-Requests': "1"
    }

    req = requests.get(dl_url, headers=headers)


    hash_md5 = hashlib.md5()
    for chunk in req.iter_content(chunk_size=128):
        hash_md5.update(chunk)
    md5sum = hash_md5.hexdigest()

    os.mkdir(pkgname)

    with open("{}/{}.install".format(pkgname, pkgname), "w") as fd:
        fd.write(install_template)

    with open("{}/PKGBUILD".format(pkgname), "w") as fd:
        fd.write(pkgbuild_template.format(pkgname=pkgname, url=args.url, dl_url=dl_url, md5=md5sum))

