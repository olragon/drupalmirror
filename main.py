#!/usr/bin/env python
"""
Tutorial: http://developer.yahoo.com/python/python-xml.html
"""
import httplib
import urllib2
from xml.dom import minidom

DRUPAL_PROJECT = 'http://updates.drupal.org/release-history/project-list/all'
XML_FILE_NAME = 'drupal-project-list-all.xml'

"""
Download xml file describe Drupal project list.
@todo: check if remote file is modified then download.
"""
def download():
    u = urllib2.urlopen(DRUPAL_PROJECT)
    f = open(XML_FILE_NAME, 'w')
    meta = u.info()
    file_size = int(meta.getheaders("Content-Length")[0])
    print "Downloading: %s Bytes: %s" % (XML_FILE_NAME, file_size)
    
    file_size_dl = 0
    block_sz = 8192
    while True:
        buffer = u.read(block_sz)
        if not buffer:
            break
    
        file_size_dl += block_sz
        f.write(buffer)
        status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
        status = status + chr(8)*(len(status)+1)
        print status,
    
    f.close()

"""
Check file's md5
"""
def md5_for_file(f, block_size=2**20):
    md5 = hashlib.md5()
    while True:
        data = f.read(block_size)
        if not data:
            break
        md5.update(data)
    return md5.digest()

"""
Parse xml file
"""
def parse_project(f):
    results = []
    elements = parse(f.open()).getroot()
    for element in elements.findall('channel/item/{%s}forecast' % WEATHER_NS):
        forecasts.append({
            'date': element.get('date'),
            'low': element.get('low'),
            'high': element.get('high'),
            'condition': element.get('text')
        })
    ycondition = rss.find('channel/item/{%s}condition' % WEATHER_NS)
    return {
        'current_condition': ycondition.get('text'),
        'current_temp': ycondition.get('temp'),
        'forecasts': forecasts,
        'title': rss.findtext('channel/title')
    }


from xml.etree.ElementTree import parse
class DrupalProjectList:
    "store drupal project list"
    def __init__(self, file = None):
        if file != None: self.file = file
    def title(self, title = None):
        return title
    def short_name(self, short_name = None):
        return short_name
    def link(self, link = None):
        return link
    def creator(self, creator = None):
        return creator
    def terms(self, terms = []):
        return terms
    def project_status(self, project_status = None):
        return project_status
    def api_versions(self, api = None):
        return title
    def buildQuery(self):
        query = "projects/project/"
        if self.title != None:
            query += self.title
        elif self.short_name != None:
            query += self.short_name() + '/'
        elif self.link != None:
            query += self.short_name() + '/'
        elif self.creator() != None:
            query += self.short_name() + '/'
        elif self.project_status() != None:
            query += self.short_name() + '/'
        elif self.api_versions() != None:
            query += 'api_versions/api_version/' + self.short_name() + '/'
        elif self.creator() != None:
            query += self.short_name() + '/'
        return query
    def result(self):
        results = []
        elements = parse(open(self.file, 'r')).getroot()
        for element in elements.findall(self.buildQuery()):
            os.spawn('git config user.name "long-nguyenl.hoang.du"')
            os.spawn('git config user.email "long-nguyenl.hoang.du@vn.asaleo-llc.com"')
            os.spawn('git clone http://git.drupal.org/project/' . element.get('') . '.git')
        pass

project = DrupalProjectList(XML_FILE_NAME)
print project.result()