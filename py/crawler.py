import requests
import jsonlines
import zipfile
import re
import sys

session = requests.Session()
session.headers = {
    'user-agent':
        'wtmsb/bgm_get',
    'Authorization': 'Bearer '+sys.argv[1],
}

def get_newest_archive():
    url = "https://api.github.com/repos/bangumi/Archive/releases/tags/archive"
    response = requests.get(url)
    release = response.json()

    newest_asset = max(release["assets"], key=lambda asset: asset["created_at"])

    asset_download_url = newest_asset["browser_download_url"]
    return asset_download_url

def fetchArchiveDump():
    r=requests.get(get_newest_archive(), stream=True)
    with open('data/dump.zip', 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024*1024):
            f.write(chunk)
    with zipfile.ZipFile('data/dump.zip', 'r') as zipObj:
        zipObj.extract('subject.jsonlines', path='data/')
        zipObj.extract('person.jsonlines', path='data/')

fetchArchiveDump()

cnt = 0
with jsonlines.open('data/subject.jsonlines') as jl:
    with jsonlines.open('./data/subject_cleaned.jsonlines', 'w') as writer:
        for line in jl:
            if line['type'] == 2:
                try:
                    temp = session.get('https://api.bgm.tv/v0/subjects/'+str(line['id'])).json()
                except:
                    print("breakpoint", line['id'])
                    break
                yr = re.search(r'(20\d\d)|(19\d\d)', str(temp['date'])) or \
                    re.search(r'(20\d\d)|(19\d\d)', next((str(i['value']) for i in temp['infobox'] if i['key']=="放送开始" or i['key']=="上映年度" or i['key']=="发售日" ), ""))
                if not yr:
                    print('\nyear not exist:', temp['id'])
                else:
                    writer.write({'year' : yr.group(), 'tags': temp['tags']})
                cnt += 1
                sys.stdout.write('\r'+str(cnt)+' subjects fetched ')
