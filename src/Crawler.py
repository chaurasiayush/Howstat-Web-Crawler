# import urllib.request, urllib.parse, urllib.error
# from bs4 import BeautifulSoup
# import ssl
#
#
#
#
# # function that returns bowling data of a match for a perticular player
# def get_bowling_data(mid, lstr, vcountry, player):
#
#     ctx = ssl.create_default_context()
#     ctx.check_hostname = False
#     ctx.verify_mode = ssl.CERT_NONE
#
#     try:
#         url = lstr + mid
#         try:
#             html = urllib.request.urlopen(url, context=ctx).read()
#             soup = BeautifulSoup(html, 'html.parser')
#
#         except:
#             print("webpage couldn't open")
#             return None
#
#         table = soup.find_all('table')
#
#         # for ltb in table:
#         #     print(len(ltb.find_all('tr')))
#
#         tb = table[0]
#         tr = tb.find_all('tr')
#         # print("total rows", len(tr))
#
#         # print(tb.prettify())
#         # for row in tr:
#         #     print(row.find('td').text.strip()[:10])
#
#         ind = 0;
#         # searching until getting the players country in rows first column
#         while tr[ind].find('td').text.strip()[:len(vcountry)] != vcountry:
#             # print(tr[ind].find('td').text.strip()[:len(vcountry)])
#             ind +=1
#
#         # searching until getting the term "Bowling" in rows first column
#         while tr[ind].find('td').text.strip()[:len("Bowling")] != "Bowling":
#             # print(tr[ind].find('td').text.strip()[:len("Bowling")])
#             ind += 1
#
#         # searching till not get players name in table
#         while tr[ind].find('td').text.strip()[:len(player)] != player:
#             ind += 1
#
#         finalcolumns = tr[ind].find_all('td')
#
#
#         # print(finalcolumns[1].text)
#         total_overs = float(finalcolumns[1].text)
#         maiden_overs = int(finalcolumns[2].text)
#         runs_given = int(finalcolumns[3].text)
#         wickets_drawn = int(finalcolumns[4].text)
#
#     except:
#         print("Error in match id: ", mid)
#         return None
#
#     return (total_overs, maiden_overs, runs_given, wickets_drawn)
#
#
# # function that returns the record of one match
# def get_total_fs(mid, lstr, country, player):
#
#     ctx = ssl.create_default_context()
#     ctx.check_hostname = False
#     ctx.verify_mode = ssl.CERT_NONE
#
#     try:
#         url = lstr + mid
#         try:
#             html = urllib.request.urlopen(url, context=ctx).read()
#             soup = BeautifulSoup(html, 'html.parser')
#
#         except:
#             print("webpage couldn't open")
#             return None
#
#         table = soup.find_all('table')
#
#         # for ltb in table:
#         #     print(len(ltb.find_all('tr')))
#
#         tb = table[0]
#         tr = tb.find_all('tr')
#         # print("total rows", len(tr))
#
#         # print(tb.prettify())
#
#         ind = 0;
#         # searching while dont get the players country in rows first column
#         while tr[ind].find('td').text.strip()[:len(country)] != country :
#             ind +=1
#             # print(tr[ind].find('td').text.strip()[:len(country)])
#
#         # searching uutill dont get players name in table
#         while tr[ind].find('td').text.strip()[:len(player)] != player:
#             ind += 1
#
#         finalcolumns = tr[ind].find_all('td')
#
#         nout = 0
#
#         if finalcolumns[1].text.strip() == 'not out':
#             nout = 1
#
#
#         runs = int(finalcolumns[2].text)
#         ballfaced = int(finalcolumns[3].text)
#         fours = int(finalcolumns[4].text)
#         sixes = int(finalcolumns[5].text)
#
#     except:
#         print("Error in match id: ", mid)
#         return None
#
#     return (nout, runs, ballfaced, fours, sixes)
#
#
# # function that returns the record of one player for all matches
# def getplayerds(player, playerID, country, versus):
#     ctx = ssl.create_default_context()
#     ctx.check_hostname = False
#     ctx.verify_mode = ssl.CERT_NONE
#
#     linkPref = "http://www.howstat.com/cricket/Statistics/Matches/MatchScorecard_ODI.asp?MatchCode="
#     url = "http://www.howstat.com/cricket/Statistics/Players/PlayerProgressBat_ODI.asp?PlayerID="+playerID
#
#     html = urllib.request.urlopen(url, context=ctx).read()
#     soup = BeautifulSoup(html, 'html.parser')
#     # Retrieve all of the anchor tags
#     # tags = soup('a')
#
#
#     table = soup.find('table', class_="TableLined")
#
#     rows = table.find_all('tr')
#     matchID = list()
#
#     for tr in rows[3:-1]:
#         columns = tr.find_all('td')
#
#         # if player has gone for batting then only look for fours and sixes
#         if columns[2].text.strip() == versus and (columns[5].text.strip()[0:1]).isnumeric():
#             # print((columns[5].text))
#
#             # extracting relative link for match score card
#             link = columns[1].find('a').get('href').strip()
#
#             # extracting and storing the match id's of the relevant matches'
#             matchID.append(link[-4:])
#
#     # print(len(matchID))
#     # for l in matchID:
#     #     print(linkPref+l)
#
#     # print(matchID)
#     print("innings Played: ",len(matchID))
#     innings = len(matchID)
#
#     noi = 0
#     runscored = 0
#     ballfaced = 0
#     fours = 0
#     sixes = 0
#     hundreds = 0
#     fifties = 0
#
#     if(innings == 0):
#         return (player, versus, 0, 0, 0, 0, 0)
#
#     for id in matchID:
#         matchrecord = get_total_fs(id, linkPref, country, player)
#
#         noi += matchrecord[0]
#         runscored += matchrecord[1]
#         ballfaced += matchrecord[2]
#         fours += matchrecord[3]
#         sixes += matchrecord[4]
#
#         if matchrecord[1]//100 >= 1:
#             hundreds += 1
#
#         elif matchrecord[1] // 50 == 1:
#             fifties += 1
#
#         # print(ds)
#
#     if innings == noi:
#         noi -= 1
#
#     print((noi, runscored, ballfaced, fours, sixes, fifties, hundreds))
#
#     ba = calc_batting_avg(runscored, innings, noi)
#     bs = calc_batting_strike_rate(runscored, ballfaced)
#     mra = calc_milestone_reaching_ability(hundreds, fifties, innings)
#     outrate = calc_outrate(noi, innings, ballfaced)
#     brpi = calc_boundary_runs_per_innings(fours, sixes, innings)
#
#     return ((player, versus, ba, bs, mra, outrate, brpi))
#
# if __name__ == '__main__':
#     # Ignore SSL certificate errors
#     ctx = ssl.create_default_context()
#     ctx.check_hostname = False
#     ctx.verify_mode = ssl.CERT_NONE
#     dfile = open('ds.txt', 'w')
#
#     playerID = ['4104', '4539', '3788', '4062', '4063', '4557', '4064', '3832', '3243', '4945', '4387', '3644', '4033', '3210', '4034', '3600', '4652', '4066', '3991', '3108', '3993', '4675', '4123', '4083', '4399', '4542', '4311', '4310', '3035', '3826', '3889', '4137', '3287', '4069', '3759', '4656', '4027', '3470', '3474', '4759', '4769', '4512', '4393', '3626', '4684', '4390', '3786']
#     player = ['M A Agarwal', 'K K Ahmed', 'R Ashwin', 'J J Bumrah', 'Y S Chahal', 'D L Chahar', 'R Dhawan', 'S Dhawan', 'M S Dhoni', 'S Dube', 'S S Iyer', 'R A Jadeja', 'K M Jadhav', 'K D Karthik', 'S Kaul', 'V Kohli', 'Kuldeep Yadav', 'D S Kulkarni', 'B Kumar', 'A Mishra', 'Mohammed Shami', 'Mohammed Siraj', 'K K Nair', 'M K Pandey', 'H H Pandya', 'R R Pant', 'Parvez Rasool', 'A R Patel', 'P A Patel', 'C A Pujara', 'A M Rahane', 'K L Rahul', 'S K Raina', 'A T Rayudu', 'W P Saha', 'N A Saini', 'V Shankar', 'I Sharma', 'R G Sharma', 'P P Shaw', 'Shubman Gill', 'B B Sran', 'S N Thakur', 'M Vijay', 'Washington Sundar', 'J Yadav', 'U T Yadav']
#     versus =  [ 'Pakistan', 'Afghanistan', 'Austria', 'United States', 'Brazil', 'Iran', 'Australia', 'Nepal', 'Spain', 'Hong Kong', 'Norway', 'Jersey', 'Iceland', 'Argentina', 'New Zealand', 'Canada', 'Netherlands',  'Bangladesh', 'Bhutan', 'West Indies', 'Maldives', 'England', 'Zimbabwe', 'South Africa', 'Sri Lanka', 'Germany']
#     country = "India"
#
#     dataset = list()
#     for i in range(0, len(playerID)):
#         for v in range(0, len(versus)):
#             pdata = getplayerds(player[i], playerID[i], country, versus[v])
#             print(pdata)
#             dataset.append(pdata)
#
#
#     dfile.write(str(dataset))