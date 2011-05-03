#!/usr/bin/env python
# -*- coding: utf8 -*-
# drupalgit
# $Id$;
#
# Clone drupal project repository
#  
# history:
# 2011-05-03 fl   created
# 
import os, sys, stat, urllib2, shlex, StringIO, subprocess 
from xml.etree.ElementTree import parse, dump

REMOTE_DRUPAL_PROJECT_LIST = 'http://updates.drupal.org/release-history/project-list/all'
LOCAL_DRUPAL_PROJECT_LIST = 'drupal-project-list-all.xml'
PATH_TO_DRUPAL_PROJECT_DIRECTORY = 'repository'

"""
Download xml file describe Drupal project list.
@todo: check if remote file is modified then download.
"""
def download():
    # Connect to drupal project list url
    r = urllib2.urlopen(REMOTE_DRUPAL_PROJECT_LIST)
    # Get remote drupal project file size
    r_size = r.info().get('Content-Length')
    print 'Remote drupal project list file size is: ' + r_size
    # Get local drupal project file size
    l_size = os.stat(LOCAL_DRUPAL_PROJECT_LIST)[stat.ST_SIZE]
    print "Local drupal project list file size is: " + str(l_size)
    
    if int(l_size) == 0:
        print "Downloading: %s Bytes: %s" % (LOCAL_DRUPAL_PROJECT_LIST, r_size)
        f = open(LOCAL_DRUPAL_PROJECT_LIST, 'w')
        file_size_dl = 0
        block_sz = 8192
        while True:
            buffer = r.read(block_sz)
            if not buffer:
                break
        
            file_size_dl += block_sz
            f.write(buffer)
            status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / int(r_size))
            status = status + chr(8) * (len(status) + 1) + '\r\n'
            print status,
        
        f.close()
        
    elif int(l_size) != int(r_size) and int(r_size) > int(l_size):
        """
        Để tránh việc ghi toàn bộ
        
        1. Đọc block remote file (r) theo từng block 8192 bytes
        2. So sánh với từng block file local (l) tương ứng
        3. Kiểm tra:
            r = l: bỏ qua và kiểm tra block tiếp theo.
            r != l: ghi block r xuống l
        """
        print 'Miss match file size. Begin update local drupal project list file.'
        
        l_file = open(LOCAL_DRUPAL_PROJECT_LIST, 'rwab+')
        file_size_dl = 0
        block_sz = 8192
        
        while True:
            r_buffer = r.read(block_sz)
            l_buffer = l_file.read(block_sz)
            
            if not r_buffer:
                break
            
            file_size_dl += block_sz
            
            if(r_buffer != l_buffer):
                l_file.seek(block_sz, block_sz - 8192)
                l_file.write(r_buffer)
                print "Path file at block " + str(file_size_dl)
            else:
                print "File block " + str(file_size_dl) + " match. Move to next block ..."
                continue
            
        l_file.close()
        
    else:
        print 'Same size! No need to update project list file.'

def chunk_report(bytes_so_far, chunk_size, total_size):
   percent = float(bytes_so_far) / total_size
   percent = round(percent*100, 2)
   sys.stdout.write("Downloaded %d of %d bytes (%0.2f%%)\r" % 
       (bytes_so_far, total_size, percent))

   if bytes_so_far >= total_size:
      sys.stdout.write('\n')

def chunk_read(response, chunk_size=8192, report_hook=None):
   total_size = response.info().getheader('Content-Length').strip()
   total_size = int(total_size)
   bytes_so_far = 0

   while 1:
      result = StringIO.StringIO()
      chunk = response.read(chunk_size)
      bytes_so_far += len(chunk)

      if not chunk:
         break

      if report_hook:
         report_hook(bytes_so_far, chunk_size, total_size)
      
      result.write(chunk)
   return result

def project_checkout(to_path = None):
    if(to_path == None): to_path = PATH_TO_DRUPAL_PROJECT_DIRECTORY
    mkdirs(to_path)
    elements = parse(open(LOCAL_DRUPAL_PROJECT_LIST, 'r')).findall('/project')
    
    n_projects = len(elements)
    n_projects_loaded = 0
    
    # Total projects
    print "Total number of Drupal projects: " + str(n_projects)
    
    
    for element in elements:
        short_name = element.findtext('short_name')
        title = element.findtext('title')
        
        path = os.getcwd() + '/' + to_path + '/' + short_name
        
        git_clone_command = "/usr/bin/env git clone http://git.drupal.org/project/" + short_name + ".git " + path
        git_fetch_command = "/usr/bin/env git fetch --all"
        
        if(os.path.exists(path)):
            args = shlex.split(git_fetch_command)
            print "Fetching project: " + title
            #print git_fetch_command
            p = subprocess.Popen(args, cwd=path, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            stdout_value = p.communicate('through stdin to stdout')[0]
            print '\tpass through:', repr(stdout_value)
            p.wait()
            #if(p.wait() != None): continue
        else:
            args = shlex.split(git_clone_command)
            print "Cloning project: " + title
            #print git_clone_command
            p = subprocess.Popen(args, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            stdout_value = p.communicate('through stdin to stdout')[0]
            print '\tpass through:', repr(stdout_value)
            p.wait()
            #if(p.wait() != None): continue
        
        status = r"%10d  [%3.2f%%]" % (n_projects_loaded, n_projects_loaded * 100. / int(n_projects))
        status = status + chr(8) * (len(status) + 1) + '\r\n'
        print status,
        
        n_projects_loaded += 1

def mkdirs(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)

if __name__ == '__main__':
    download()
    project_checkout(PATH_TO_DRUPAL_PROJECT_DIRECTORY)
