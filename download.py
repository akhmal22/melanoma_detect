import requests


class ISICApi(object):
    def __init__(self, hostname='https://isic-archive.com',
                 username=None, password=None):
        self.baseUrl = f'{hostname}/api/v1'
        self.authToken = None

        if username is not None:
            if password is None:
                password = input(f'Password for user "{username}":')
            self.authToken = self._login(username, password)

    def _makeUrl(self, endpoint):
        return f'{self.baseUrl}/{endpoint}'

    def _login(self, username, password):
        authResponse = requests.get(
            self._makeUrl('user/authentication'),
            auth=(username, password)
        )
        if not authResponse.ok:
            raise Exception(f'Login error: {authResponse.json()["message"]}')

        authToken = authResponse.json()['authToken']['token']
        return authToken

    def get(self, endpoint):
        url = self._makeUrl(endpoint)
        headers = {'Girder-Token': self.authToken} if self.authToken else None
        return requests.get(url, headers=headers)

    def getJson(self, endpoint):
        return self.get(endpoint).json()

    def getJsonList(self, endpoint):
        endpoint += '&' if '?' in endpoint else '?'
        LIMIT = 50
        offset = 0
        while True:
            resp = self.get(
                f'{endpoint}limit={LIMIT:d}&offset={offset:d}'
            ).json()
            if not resp:
                break
            for elem in resp:
                yield elem
            offset += LIMIT

            

import urllib
import os

api = ISICApi()
savePath = 'ISICArchive/'
savePathB = 'ISICArchive/benign/'
savePathM = 'ISICArchive/malignant/'
savePathO = 'ISICArchive/others/'

if not os.path.exists(savePath):
    os.makedirs(savePath)
    if not os.path.exists(savePathB):
        os.makedirs(savePathB)
    if not os.path.exists(savePathM):
        os.makedirs(savePathM)
    if not os.path.exists(savePathO):
        os.makedirs(savePathO)
        
        
 
imageList = api.getJson('image?limit=23000&offset=0&sort=name')

print('Downloading %s images' % len(imageList))
imageDetails = []
for image in imageList:
    print('{} - {} '.format(image['_id'],image['name']))
    imageDetail = api.getJson('image/%s' % image['_id'])
    try:
        imageDetail['meta']['clinical']['benign_malignant']
        print(imageDetail['meta']['clinical']['benign_malignant'])
        if imageDetail['meta']['clinical']['benign_malignant'] == 'malignant':
            imageFileResp = api.get('image/%s/download' % image['_id'])
            imageFileResp.raise_for_status()
            imageFileOutputPath = os.path.join(savePathM, '{} - {}.jpg'.format(image['name'],imageDetail['meta']['clinical']['benign_malignant']))
            with open(imageFileOutputPath, 'wb') as imageFileOutputStream:
                for chunk in imageFileResp:
                    imageFileOutputStream.write(chunk)
    except:
        print("Error")