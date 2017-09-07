#coding=utf-8


#import Modules
from urlparse import urlparse, urlunparse
import urllib, urllib2, os,json, re

#todo: get the server
agsUrl = "https://www.seanpc.com:6443/arcgis"


#todo: get parameters
portalUrl = "https://www.seanpc.com/arcgis"

username = 'portaladmin'
password = 'esrichina'

folder = 'd:\\'

#todo: generate Token
def generateToken(username, password, agsUrl):
    parameters = urllib.urlencode({'username' : username,
                                   'password' : password,
                                   'client' : 'referer',
                                   'referer': agsUrl,
                                   'expiration': 60, #minutes
                                   'f' : 'json'})
    response = urllib2.urlopen(url,parameters).read()
    try:
        jsonResponse = json.loads(response)
        if 'token' in jsonResponse:
            return jsonResponse['token']
        elif 'error' in jsonResponse:
            print jsonResponse['error']['message']
            for detail in jsonResponse['error']['details']:
                print detail
    except ValueError, e:
        print 'An unspecified error occurred.'
        print e


##todo: START HERE - it all starts here

#place a banner in the code
print '***\nList ArcGIS Services DataSource Content\n***\n'


#todo: generate ArcGIS admin Token
url = portalUrl + '/sharing/rest/generateToken?'
token = generateToken(username, password, url)


##todo: write to File
fs = open(folder + os.path.sep + 'ArcGISContent.csv', 'w+')
fs.write('文件夹,服务名称,类型,是否引用，数据源\n')


#todo: get and process Arcgis Services
parameters = urllib.urlencode({'f' : 'json', 'token': token})
rootUrl = agsUrl + '/admin/services'
response = urllib2.urlopen(rootUrl, parameters).read()
jsonResponse = json.loads(response)


#todo: loop services
for svc in jsonResponse['services']:
    serviceUrl =  agsUrl + '/admin/services' + svc['folderName'] + \
                  urllib2.quote(svc['serviceName'].encode('utf-8')) + '.' + svc['type'] + '/iteminfo/manifest/manifest.json'
    if svc['type'] in ['MapServer', 'ImageServer', 'FeatureServer']:
        svcResponse = urllib2.urlopen(serviceUrl,parameters).read()
        svcJsonResponse = json.loads(svcResponse)
        if svcJsonResponse.has_key('databases') :
            for db in svcJsonResponse['databases']:
                fs.write('{0},{1},{2},{3},{4}\n'.format('', svc['serviceName'].encode('utf-8'), svc['type'],
                                                            db['byReference'],db['onServerConnectionString']))



#todo: loop folders containing services
for folder in jsonResponse['folders']:
    folderUrl = agsUrl + '/admin/services' + '/' + folder
    fldResponse = urllib2.urlopen(folderUrl, parameters).read()
    fldJsonResponse = json.loads(fldResponse)
    for svc in fldJsonResponse['services']:
        if svc['type'] in ['MapServer', 'ImageServer', 'FeatureServer']:
            serviceUrl = agsUrl + '/admin/services' + '/' + folder + '/' + \
                         urllib2.quote(svc['serviceName'].encode('utf-8')) + '.' + svc['type'] + '/iteminfo/manifest/manifest.json'
            svcResponse = urllib2.urlopen(serviceUrl, parameters).read()
            svcJsonResponse = json.loads(svcResponse)
            if svcJsonResponse.has_key('databases'):
                for db in svcJsonResponse['databases']:
                    fs.write('{0},{1},{2},{3},{4}\n'.format(folder, svc['serviceName'].encode('utf-8'), svc['type'],
                                                            db['byReference'],db['onServerConnectionString']))


##todo: close the file
fs.close()


print '\ncompleted'
