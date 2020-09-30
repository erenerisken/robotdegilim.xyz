import json

with open("data.json","r",encoding="UTF-8") as f:
    string = f.read()

string = string.replace("\\u0130",u'\u0130')
string = string.replace("\\u00d6",u'\u00d6')
string = string.replace("\\u00dc",u'\u00dc')
string = string.replace("\\u015e",u'\u015e')
string = string.replace("\\u00c7",u'\u00c7')
string = string.replace("\\u011e",u'\u011e')
string = string.replace("\\u00c2",u'\u00c2')


with open("data.json","w",encoding="UTF-8") as f:
    f.write(string)
