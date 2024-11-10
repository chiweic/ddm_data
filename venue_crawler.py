# extract all venue from website...
import requests # type: ignore
import logging
from bs4 import BeautifulSoup
import json

field_mapping = {'電話':'telephone', '地址':'address', '傳真':'fax', '信箱':'email'}

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    # send a post to create venue, param is for get, data is for post
    endpoint = 'http://127.0.0.1:8000/v1/venues'
    headers = headers = {'content-type' : 'application/json'}
    # set up to crawl all venues from main website
    root_url = 'https://www.ddm.org.tw/xclocation?xsmsid=0K296464423399846372&region=1'
    # LocationList tw
    soup = BeautifulSoup(requests.get(root_url).text, "html.parser")
    elem = soup.find('div', {'class':'LocationList tw'})
    for venue in elem.find_all('div', {'class':'item'}):
        name = venue.find('div', {'class':'title'}).text
        logging.info('processing:{}'.format(name))
        data = {'name': name}
        # when name contain '/' meaning both organization shared same venue
        # we can dup the contact information, but use unique name
        # contaxts:
        contacts = venue.find('ul',{'class':'contact_info'})
        contacts_lines = contacts.text.strip().splitlines()
        # example of this string...
        for line in contacts_lines:
            fields = line.split('：')
            if fields[0] in field_mapping:
                data[field_mapping[fields[0]]]=' '.join(fields[1:])
        
        if '/' in name:
            for n in name.split('/'):
                data['name']=n.strip()
                logging.info('adding:{}'.format(data))
                response = requests.post(url=endpoint, headers=headers, json=data)
                if response.status_code != 200:
                    logging.error('entrt problem')

        else:
            logging.info('adding:{}'.format(data))
            response = requests.post(url=endpoint, headers=headers, json=data)
            if response.status_code != 200:
                    logging.error('entrt problem')