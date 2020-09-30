import requests
from bs4 import BeautifulSoup
import time
import re
import json
from unidecode import unidecode

s = requests.Session()
headers = requests.utils.default_headers()
headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 7.0; Win64; x64; rv:3.0b2pre) Gecko/20110203 Firefox/4.0b12pre",
			"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
			"Pragma": "no-cache"})


url = "https://oibs.metu.edu.tr/cgi-bin/View_Program_Details_58/View_Program_Details_58.cgi"
#index_text = s.get(url, headers=headers).content.decode("utf-8")
data = {"SubmitName":"Submit", "SaFormName" : "action_index__Findex_html"}
#SubmitName=Submit&SaFormName=action_index__Findex_html
#data = {"text_usercode":"e231066", "text_password": "0kvDFfD1","submit_auth":"Login","hidden_redir":"Login"}
#text_usercode=e231066&text_password=0kvDFfD1&submit_auth=Login&hidden_redir=Login
r = s.post(url,data)
time.sleep(2)
with open("1.html","w",encoding="utf-8") as f:
    f.write(r.text)

courses = ["Must Courses","Elective Courses"]
prefixes = {'219': u'GENE', '956': u'OCEA', '450': u'FLE', '612': u'PERS', '451': u'TEFL', '810': u'GWS', '811': u'UPL', '814': u'SA', '815': u'ARS', '816': u'MCS', '817': u'FPSY', '453': u'PES', '120': u'ARCH', '121': u'CRP', '125': u'ID', '420': u'SSME', '363': u'STAS', '379': u'ARC', '378': u'GPC', '410': u'ELE', '411': u'ECE', '371': u'PSYC', '370': u'FRN', '372': u'SOCL', '821': u'ELIT', '820': u'ELT', '377': u'PHL', '822': u'ESME', '312': u'BA', '311': u'ECON', '310': u'ADM', '316': u'BAS', '315': u'GIA', '314': u'IR', '391': u'ENLT', '390': u'SEES', '832': u'MES', '833': u'EUS', '795': u'TKPR', '831': u'STPS', '837': u'EMBA', '834': u'HRDE', '835': u'EAS', '838': u'EI', '839': u'SPL', '798': u'ENEL', '368': u'EDUS', '369': u'GRM', '366': u'EFL', '367': u'CHME', '364': u'CVE', '365': u'MECH', '362': u'HST', '910': u'CSEC', '360': u'CHM', '361': u'TUR', '855': u'UD', '246': u'STAT', '384': u'ASE', '240': u'HIST', '386': u'IDS', '902': u'COGS', '901': u'IS', '843': u'LNA', '842': u'ASN', '841': u'GTSS', '840': u'SAN', '375': u'ART', '908': u'BIN', '909': u'GATE', '374': u'PNGE', '643': u'THEA', '642': u'TURK', '644': u'SLTP', '241': u'PHIL', '376': u'CTE', '430': u'CEIT', '385': u'SPN', '573': u'FDE', '572': u'AEE', '571': u'CENG', '570': u'METE', '454': u'EDS', '880': u'OR', '629': u'TFL', '854': u'BS', '853': u'CP', '856': u'CONS', '857': u'IDDI', '852': u'RP', '970': u'IAM', '858': u'ARCD', '651': u'MUS', '568': u'IE', '569': u'ME', '560': u'ENVE', '561': u'ES', '562': u'CE', '563': u'CHE', '564': u'GEOE', '565': u'MINE', '566': u'PETE', '567': u'EE', '906': u'MI', '904': u'ION', '861': u'BTEC', '860': u'BCH', '863': u'ARME', '862': u'PST', '865': u'GGIT', '864': u'ASTR', '867': u'SE', '866': u'EM', '905': u'SM', '605': u'JA', '604': u'GERM', '607': u'RUS', '606': u'ITAL', '603': u'FREN', '608': u'SPAN', '238': u'BIOL', '234': u'CHEM', '236': u'MATH', '230': u'PHYS', '232': u'SOC', '233': u'PSY', '878': u'NSNT', '876': u'MDM', '950': u'MASC', '874': u'ESS', '872': u'BME', '873': u'EQS', '870': u'CEME', '871': u'MNT', '354': u'PSIR', '639': u'ENG', '610': u'GRE', '611': u'CHN', '357': u'MAT', '356': u'EEE', '355': u'CNG', '954': u'MBIO', '353': u'BUS', '352': u'ECO', '877': u'OHS', '801': u'AH', '358': u'PHY', '359': u'ENGL', '682': u'INST', "976": "IAM", "836": "PHIL", "459": "BED", "373": "BIO", "351": "BUSD", "952": "MASC", "422": "CHED", "971": "IAM", "825": "EDS", "875": "EQS", "824": "EDS", "797": "EEE", "401": "ECE", "413": "EME", "412": "ESE", "799": "ENOT", "383": "ESC", "382": "ENV", "884": "ENVM", "973": "FM", "800": "SBE", "869": "HE", "791": "AUTO", "602": "ARAB", "951": "MASC", "421": "PHED", "972": "SC", "907": "WBLS"}
data = {"SubmitName":"Must Courses","radio_program_code":120,"hidden_autologin":1,"SaFormName":"action_programs__FPrograms_html"}
#SubmitName=Must+Courses&radio_program_code=120&hidden_autologin=1&SaFormName=action_programs__FPrograms_html
count=0
jsondata = {}
for j in prefixes.keys():
    jsondata[prefixes[j]] = {"Department Code": j,"Courses":{courses[0]:[],courses[1]:[]}}
    for i in courses:
        if i == "Elective Courses":
            continue
        data = {"SubmitName":i,"radio_program_code":j,"hidden_autologin":1,"SaFormName":"action_programs__FPrograms_html"}
        r = s.post(url,data)

        soup = BeautifulSoup(r.text,features="html.parser")
        data = []
        table = soup.findAll('table')
        try:
            table = table[4]#the correct one
        except:
            continue #If there is no course
        #table_body = table.find('tbody')
        rows = table.findAll('tr')
        del rows[0]
        for row in rows:
            arr = {}
            cells = row.findAll("td")
            arr["Set No"]       =    cells[0].find(text=True)
            arr["Course Code"]  =    cells[1].find(text=True)
            arr["Course Name"]  =    cells[2].find(text=True)
            arr["Credit"]       =    cells[3].find(text=True)
            arr["Sem No"]       =    cells[4].find(text=True)
            arr["Year"]         =    cells[5].find(text=True)
            arr["Set No"] = unidecode(arr["Set No"])[:-1]   
            arr["Course Code"] = unidecode(arr["Course Code"])[:-1]   
            arr["Course Name"] = unidecode(arr["Course Name"])[:-1]  
            arr["Credit"] = unidecode(arr["Credit"])[:-1]   
            arr["Sem No"] = unidecode(arr["Sem No"])[:-1]   
            arr["Year"] = unidecode(arr["Year"])[:-1]   
            jsondata[prefixes[j]]["Courses"][i].append(arr)

for j in prefixes.keys():
    for i in courses:
        if i == "Must Courses":
            continue
        data = {"SubmitName":i,"radio_program_code":j,"hidden_autologin":1,"SaFormName":"action_programs__FPrograms_html"}
        r = s.post(url,data)

        soup = BeautifulSoup(r.text,features="html.parser")
        data = []
        table = soup.findAll('table')
        try:
            table = table[2]#the correct one
        except:
            continue #If there is no course
        #table_body = table.find('tbody')
        rows = table.findAll('tr')
        del rows[0]
        for row in rows:
            arr = {}
            cells = row.findAll("td")
            arr["Course Code"]  =    cells[0].find(text=True)
            arr["Course Name"]  =    cells[1].find(text=True)
            arr["Credit"]       =    cells[2].find(text=True)
            arr["Category"]     =    cells[3].find(text=True)
            arr["Position"]     =    cells[4].find(text=True)
            arr["Course Code"] = unidecode(arr["Course Code"])[:-1]   
            arr["Course Name"] = unidecode(arr["Course Name"])[:-1]  
            arr["Credit"] = unidecode(arr["Credit"])[:-1]   
            arr["Category"] = unidecode(arr["Category"])[:-1]   
            arr["Position"] = unidecode(arr["Position"])[:-1]   
            jsondata[prefixes[j]]["Courses"][i].append(arr)

with open('nte.json', 'w') as outfile:
    json.dump(jsondata, outfile)



exit()