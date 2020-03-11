import requests
import json
from datetime import datetime
from datetime import date, timedelta
import csv
import re 
import urllib.parse
def csv_writer(data, path):
    with open(path, "w", newline='') as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        for line in data:
            writer.writerow(line)

headers={
	'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
	'Accept-Encoding': 'br',
	'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',

}
now_data=(date.today())
end_data=(date.today() - timedelta(days=7))
url=f'https://amtsblatt.be.ch/api/v1/publications?allowRubricSelection=true&includeContent=false&pageRequest.page=0&pageRequest.size=100&\
publicationDate.end={now_data}&publicationDate.start={end_data}&publicationStates=PUBLISHED&publicationStates=CANCELLED\
&rubrics=BP-BE&searchPeriod=LAST7DAYS&subRubrics=BP-BE10&subRubrics=BP-BE20&tenant=kabbe'


response = requests.get(url)
if response.status_code == 200:
    print('Success!')
elif response.status_code == 404:
    print('Not Found.')
a = response.content.decode('utf8')#.decode('cp1251')
json_string = json.loads(a)



data = ["canton,url,amtsblatt,date,type,content,municipality,number,bauherr,bh_name,bh_address,bh_street,\
		bh_number,bh_place,bh_plz,bh_lon,bh_lat,projektverfasser,pv_address,pv_name,pv_street,pv_number,\
		pv_place,pv_plz,pv_lon,pv_lat,construction,con_plot,con_street,lon,lat,zone,exception,coord,".split(",")
		]

kk=0
all_items=[]
for i in json_string['content']:
	items=[]
	j=i['meta']
	items.append(j['cantons'][0])
	items.append('https://www.amtsblatt.zh.ch/#!/search/publications/detail/'+j['id'])
	items.append('')
	items.append(j['publicationDate'].split('T')[0])
	items.append('Baupublikation')
	items.append('---content---')
	try:
		print(j['registrationOffice']['displayName'])
		items.append(j['registrationOffice']['displayName'])
	except:
		items.append('---')
	items.append(j['publicationNumber'])

	url=f'https://amtsblatt.be.ch/api/v1/publications/{j["id"]}/view'
	response = requests.get(url)
	a = response.content.decode('cp1251', errors='ignore')
	json_string2 = json.loads(a)

	bauherr=(json_string2['fields'][1]['fields'][0]['fields'][0]['value']['defaultValue'])

	bauherr=(bauherr.replace('<div>',''))
	bauherr2=bauherr.replace('<br />',' ').replace('<br/>',' ').replace('</div></div>','')
	items.append(bauherr2)

	bh_name=re.search(r'.+?(?=<)', bauherr)[0]
	items.append(bh_name)

	try:
		bh_address=re.search(r'(?<=<br/> ).+(?=</div></div>)', bauherr)[0].replace('<br />',', ').replace('<br/>',', ')
	except:
		bh_address=re.search(r'(?<=br />).+(?=</div></div>)', bauherr)[0].replace('<br />',', ').replace('<br/>',', ')
			
	items.append(bh_address)

	try:
		bh_street=re.search(r'(?<=>)(| )(([^></]+ ){0,4}[^></]+) \d{1,5}(\w|)(<| <|,)', bauherr)[0]
		bh_street=bh_street.replace(' <','').replace('<','').replace(',','')
	except Exception as e:
		bh_street=''	
	bh_number=bh_street.split(' ')[-1]	
	bh_street=bh_street.replace(bh_number,'')
	items.append(bh_street)
	items.append(bh_number)
	
	bh_temp=re.search(r'\d{4} [^></ ]+', bauherr)[0]
	bh_plz=bh_temp.split(' ')[0]
	bh_place=bh_temp.split(' ')[1]
	items.append(bh_place)
	items.append(bh_plz)



	try:
		coord=(f'{bh_street}+{bh_number}+{bh_plz}+{bh_place}').replace(' ','+')
		#coord=urllib.parse.quote_plus(f'{bh_street} {bh_number} {bh_place}')
		url=f'https://nominatim.openstreetmap.org/search?q={coord}&format=json'
		response = requests.get(url)		
		response = response.content.decode('cp1251', errors='ignore')
		lat=re.search(r'(?<=lat\":\").+?(?=\")', response)[0]
		lon=re.search(r'(?<=lon\":\").+?(?=\")', response)[0]
	except Exception as e:
			lat,lon='',''
	
	kk+=1	
	items.append(lon)
	items.append(lat)
	all_items.append(items)

print(kk)

for i in all_items:
	data.append(i)

path = "output.csv"
csv_writer(data, path)


