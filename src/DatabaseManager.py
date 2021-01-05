import sqlite3
import src.PlayerName as pname
import urllib.request, urllib.parse, urllib.error
from bs4 import BeautifulSoup, SoupStrainer
import ssl
import re


conn = sqlite3.connect("Player Database/ODIRecords.db")
curr = conn.cursor()

# curr.execute("select html from match_html where match_code == 1907")

# html = curr.fetchone()[0]

print("opened database successfully")

def toint(num):

    if len(num) == 0:
        return 0
    else:
        return int(num)

def insert_match_html():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    query = 'select substr("0000"|| match_code, -4) from matches_in_series_toinsert'
    curr.execute(query)
    matches = curr.fetchall()

    for mid in matches:

        try:
            url = 'http://www.howstat.com/cricket/Statistics/Matches/MatchScorecard_ODI.asp?MatchCode=' + str(mid[0]) + '&Print=Y'
            html = urllib.request.urlopen(url, context=ctx).read()

            # print(html.decode('UTF-8'))
            query = 'insert into match_html values(?, ?)'
            arguments = (mid[0], html)

            curr.execute(query, arguments)
            print('DONE  : ENTERED FOR MATCH ID -', mid[0])
            conn.commit()

        except Exception as e:
            print('ERROR : SKIPPED FOR MATCH ID -', mid[0], e)


def insertcountry():
    countries =  [ 'India', 'Pakistan', 'Afghanistan', 'Australia', 'New Zealand',  'Bangladesh', 'West Indies', 'England', 'Zimbabwe', 'South Africa', 'Sri Lanka']
    countries = sorted(countries)

    for country in countries:
        query = "Insert into country_data(cname) values('"+country + "')"
        # print(query)
        rec = conn.execute(query)

    conn.commit()


def insert_current_players(cntry):
    # fetching player data who are already in database
    dbplayers = list()
    curr.execute("select pid from player_data")
    for tmp in curr.fetchall():
        dbplayers.append(tmp[0])

    # fetching country id from db
    curr.execute("select cid from country_data where cname == \""+cntry+"\"")
    cid = curr.fetchone()[0]

    # retrieving data from internet
    pdata = pname.getPlayerData(cntry)

    # print(dbplayers)
    for i in range(0, len(pdata[0])):
        if int(pdata[0][i]) in dbplayers:
            print("skipping record ("+pdata[0][i]+", '"+pdata[1][i]+"', "+pdata[2][i]+", "+str(cid)+")")
            continue

        else:
            query = "Insert into player_data(pid, name, yob, cid) values("+pdata[0][i]+", '"+pdata[1][i]+"', "+pdata[2][i]+", "+str(cid)+")"
            conn.execute(query)
            print("inserted record ("+pdata[0][i]+", '"+pdata[1][i]+"', "+pdata[2][i]+", "+str(cid)+")")

    conn.commit()
    # curr.execute("select * from PlayerData")
    # result = curr.fetchall()
    # # print(len(result))
    # for d in result:
    #     print(d)


def insert_series_record(country):
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    url = "http://www.howstat.com/cricket/Statistics/Series/SeriesListCountry_ODI.asp?A=" + country + "&B=XXX&W=X#odis"

    html = urllib.request.urlopen(url, context=ctx).read()
    strainer = SoupStrainer('table', class_="TableLined")  # "added"
    soup = BeautifulSoup(html, 'html.parser', parse_only=strainer)
    # Retrieve all of the anchor tags
    # tags = soup('a')

    table = soup.find("table")

    rows = table.find_all('tr')

    for row in rows[1:-2]:

        columns = row.find_all('td')

        series_code = columns[0].find('a').get('href')[-4:]

        # print(series_code)

        countries = columns[0].text.strip().split(' ', 1)[1].split('v.')
        scnt1 = countries[0].strip()
        scnt2 = countries[1].strip()

        query = "select cid from country_data where cname == \""+ scnt1.strip()+ "\""
        curr.execute(query)
        cnt1 = curr.fetchone()

        query = "select cid from country_data where cname == \"" + scnt2.strip() + "\""
        curr.execute(query)
        cnt2 = curr.fetchone()

        if cnt1 is not None and cnt2 is not None:
            cnt1 = cnt1[0]
            cnt2 = cnt2[0]
            matches = columns[2].text.strip()

            temp = re.compile("([A-Za-z ]+)+ +([0-9]+-[0-9]+)")
            result = temp.match(columns[3].text.strip()).groups()

            # result = columns[3].text.strip().split(" ", -1)
            if result[0] == scnt1:
                score = result[1].split('-')
                cnt1_wins = score[0]
                cnt2_wins = score[1]

            else:
                score = result[1].split('-')
                cnt1_wins = score[1]
                cnt2_wins = score[0]

            # print(result)

            query = "Insert into series_record values(?, ?, ?, ?, ?, ?)"
            var = (series_code, cnt1, cnt2, matches, cnt1_wins, cnt2_wins)
            try:
                curr.execute(query, var)
                print('DONE :: RECORD INSERTED FOR SERIES CODE: ', series_code)
            except:
                print('FAILED :: RECORD ALREADY EXIST FOR SERIES CODE: ', series_code)
            # conn.commit()

        # print(scnt1, " ", scnt2, " ", cnt1_wins, " ", cnt2_wins, " ", columns[3].text.strip())


def insert_series_match_codes(series_code):
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    url = "http://www.howstat.com/cricket/Statistics/Series/SeriesStats_ODI.asp?SeriesCode=" + series_code

    html = urllib.request.urlopen(url, context=ctx).read()
    strainer = SoupStrainer('table', class_="TableLined")  # "added"
    soup = BeautifulSoup(html, 'html.parser', parse_only=strainer)
    # Retrieve all of the anchor tags
    # tags = soup('a')

    table = soup.find('table')
    rows = table.findAll('tr')

    print("---------------------------------------------------------------------------------------------------")
    print("                                          SERIES CODE: ", series_code)
    print("---------------------------------------------------------------------------------------------------")

    for row in rows[1:]:
        columns  = row.find_all('td')

        date = columns[0].text.strip()
        match_code = columns[1].find('a').get('href').strip()[-4:]
        result = columns[3].text.strip()

        query = '''Insert into matches_in_series values(?, ?, ?, ?)'''
        arguments = (series_code, match_code, date, result)

        curr.execute(query, arguments)
        print("Inserted for Match code: ", match_code)

    print()


def series_match_code_inserter():
    query = '''select substr(0000 || series_code, -4) from series_record_toinsert'''
    curr.execute(query)
    rs = curr.fetchall()
    for series_code in rs:

        insert_series_match_codes(series_code[0])
        conn.commit()


def get_batting_rec_row(row, cid):

    columns = row.find_all('td')
    flag = columns[0].text.strip()

    notout = 0

    if (flag == 'Extras'):
        flag = ""
        playername = re.findall('[A-Z-a-z ]*', columns[0].text.strip())[0]
        pid = -cid
        pruns = toint(columns[2].text.strip())
        ballfaced = 0
        fours = 0
        sixes = 0

    else:
        playername = re.findall('[A-Z-a-z ]*', columns[0].text.strip())[0]
        pid = toint(columns[0].find('a').get('href').strip()[-4:])
        notout = 1 if columns[1].text.strip() == 'not out' else 0
        pruns = toint(columns[2].text.strip())
        ballfaced = toint(columns[3].text.strip())
        fours = toint(columns[4].text.strip())
        sixes = toint(columns[5].text.strip())

        # print([pid, playername, notout, pruns, ballfaced, fours, sixes])
    return [pid, playername, notout, pruns, ballfaced, fours, sixes]


def get_bowlling_rec_row(row):
    columns = row.find_all('td')
    playername = re.findall('[A-Z-a-z ]*', columns[0].text.strip())[0]
    pid = int(columns[0].find('a').get('href').strip()[-4:])
    overs = float(columns[1].text.strip())
    maidenovers = float(columns[2].text.strip())
    runsgiven = int(columns[3].text.strip())
    wicketstaken = int(columns[4].text.strip())

    return [pid, overs, maidenovers, runsgiven, wicketstaken]


def get_match_scrorecard(html):

    try:
        # url = 'http://www.howstat.com/cricket/Statistics/Matches/MatchScorecard_ODI.asp?MatchCode=' + str(
        # 1069) + '&Print=Y'
        # html = urllib.request.urlopen(url, context=ctx).read()
        soup = BeautifulSoup(html, 'html')

    except:
        print("webpage couldn't open")
        return None

    playerrecord = dict()
    table = soup.find_all('table')
    ind = 1

    # for t in table:
    #     print("total rows: ", len(t.find_all('tr', recursive= False)))

    cntry = table[0].find_all('td', {'class' : "ScoreCardBanner2"})
    cntry = cntry[0].get_text().split(' v ')
    cntry[1] = re.findall('[A-Za-z ]+', cntry[1])[0].strip()
    cntry[0] = re.findall('[A-Za-z ]+', cntry[0])[0].strip()
    print(cntry)

    tb = table[3]
    rows = tb.findChildren('tr', recursive= False)

    # getting country id from database
    country = rows[0].find('td').text.strip()
    curr.execute("select cid from country_data where cname == \"" + country +"\"")
    cid = curr.fetchone()[0]

    # for batting table team 1
    while True:

        record = list()
        bat = get_batting_rec_row(rows[ind], cid)
        bat.insert(0, cid)
        record.append(bat)
        playerrecord[bat[1]] = record
        ind = ind + 1

        if (bat[2] == 'Extras'):
            flag = ""
            break

    # for bowlling table team 2
    brows = table[5].find_all('tr')

    for ind in range(1, len(brows)):

        bowlrecord = list()

        bowl = get_bowlling_rec_row(brows[ind])
        pid = bowl[0]
        bowl.pop(0)
        bowlrecord.append(bowl)
        playerrecord[pid] = bowlrecord

    # getting cid for team 2
    while ind < 100:
        country = ""
        try:
            country = re.findall('[A-Z][A-Z-a-z ]*[a-z]', rows[ind].find('td', {'class': 'TextBlackBold8'}).get_text())[0]
        except:
            # print(ind)
            2
        # print(country)
        ind = ind + 1

        if(country == cntry[0] or country == cntry[1]):
            break

    curr.execute("select cid from country_data where cname == \"" + country + "\"")
    cid =  curr.fetchone()[0]

    # for batting table team 2
    # ind = ind + 2
    while True:
        bat = get_batting_rec_row(rows[ind], cid)
        pid = bat[0]
        bat.insert(0, cid)

        battingrec = playerrecord.get(pid)

        if battingrec is None:
            battingrec = [bat, [0, 0, 0, 0]]

        else:
            battingrec.insert(0, bat)

        playerrecord[pid] = battingrec

        ind = ind + 1
        if (bat[2] == 'Extras'):
            flag = ""
            break

    # for bowlling table team 1
    brows = table[7].find_all('tr')

    for i in range(1, len(brows)):
        bowlrecord = list()

        bowl = get_bowlling_rec_row(brows[i])
        bowlrecord.append(bowl)
        pid = bowl[0]
        bowl.pop(0)
        record = playerrecord.get(pid)

        record.insert(1, bowl)

    # insert zeros for bowlling record of remaining team 1 players
    for key in playerrecord.keys():
        if len(playerrecord[key]) == 1:
            playerrecord[key].insert(1, [0, 0, 0, 0])

    return playerrecord


def insert_scorecard():
    # query = ("select * from match_html where match_code == ?")
    # argument = (1002,)
    # curr.execute(query, argument)

    query = ("select * from match_html")
    curr.execute(query)

    error = list()
    # 1004, 1084, 1086, 1089, 1168, 1179, 1185, 1214, 1216, 1296, 1307, 1458, 1461, 1665, 1748, 1789, 1790, 1873, 1902, 1982, 1983, 2297, 2333, 2338, 2384, 2385, 2388, 2392, 2393, 2394, 2395, 2396, 2398, 2399, 2423, 2426, 2428, 2430, 2432, 2552, 2557, 2627, 2629, 2690, 2700, 2727, 2738, 2742, 2903, 2905, 2940, 2943, 2945, 3040
    abmatches = list()
    scorecards = curr.fetchall()
    # print(htmls)
    for sc in scorecards:
        print(sc[0])
        records = {}
        # records = get_match_scrorecard(sc[1])
        soup = BeautifulSoup(sc[1], 'html')

        tab = soup.find_all('table')
        # soup = BeautifulSoup(str(tab[3]), )
        #
        # tab = soup.find_all('table')
        print('total table ', len(tab))
        # print(len(tab[3].find_all('tr')))

        try:
            records = get_match_scrorecard(sc[1])

        except Exception as e:

            print(e)

            if len(tab) < 7:
                abmatches.append(sc[0])
            else:
                error.append(sc[0])

        # for t in tab:
        #     print(len(t.findChildren('tr', recursive=False)))

        for pid in records.keys():
            # print(records[pid])
            psc = records[pid]

            # if pid > 0:
            #     ps = records[pid][0]
            #     query1 = 'insert into player_data(pid, name, yob, cid) values(?, ?, ?,  ?)'
            #     att1 = (ps[1], ps[2], 1990, ps[0])
            #     try:
            #         curr.execute(query1, att1)
            #         print('DONE    : PLAYER INSERTED - ', pid)
            #     except sqlite3.IntegrityError:
            #         print('SKIPPED : ALREADY EXIST   - ', pid)

            query2 = 'insert into match_scorecard values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
            attr2 = (sc[0], psc[0][1], psc[0][3], psc[0][4], psc[0][5], psc[0][6], psc[0][7],
                     psc[1][0], psc[1][1], psc[1][2], psc[1][3])
            try:
                curr.execute(query2, attr2)
                print('DONE    : PLAYER RECORD INSERTED - ', pid)
            except sqlite3.IntegrityError:
                print("SKIPPING PLAYER...")
        conn.commit()

        print(error)
        print(len(error))

        print(abmatches)
        print(len(abmatches))

# main program starts here
# insert_series_record("ZIM")
# series_match_code_inserter()
# get_match_scrorecard('4398')
insert_scorecard()
# insert_match_html()







