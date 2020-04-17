import urllib.request, urllib.parse, urllib.error
from bs4 import BeautifulSoup
import ssl

def getPlayerData(cnt):
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    url = "http://www.howstat.com.au/cricket/Statistics/Players/PlayerListCurrent.asp"

    html = urllib.request.urlopen(url, context=ctx).read()
    soup = BeautifulSoup(html, 'html.parser')

    table = soup.find('table', class_='TableLined')

    rows = table.find_all('tr')

    player = list()
    playerYob = list()
    playerID = list()
    country = set()

    for r in rows[:-1]:
        cell = r.find_all('td')
        country.add(cell[2].text.strip())
        if(cell[2].text.strip() == cnt and cell[4].text.strip().isnumeric()):

            name = cell[0].text.strip()
            if ',' in name:
                name = name.split(',')
                # print(name[1].strip()+" "+name[0])
                player.append(name[1].strip()+" "+name[0])
            else:
                # print(name)
                player.append(name)

            yob = cell[1].text.strip()[-4:]
            playerYob.append(yob)
            link = cell[0].find('a').get('href')
            # print(link[-4:])
            playerID.append(link[-4:])
    return [playerID, player, playerYob]


# print(getPlayerData('India'))