#!/usr/bin/env python
# -*- coding: utf8 -*-
# drupalgit
# $Id$;
#
# Clone drupal project repository
# 
# requirements:
#     git
#        Ubuntu: sudo apt-get install gitosis
#     
# history:
# 2011-05-03      created
#                 change file name main.py to drupalmirror.py
# 
# 2011-10-03      remove code continue download xml, validate xml
#                 add function export to gitweb

import os, sys, stat, urllib2, shlex, StringIO, subprocess, re
import xml.etree.ElementTree as etree
import argparse

"""
Download xml file describe Drupal project list.
@todo: check if remote file is modified then download.
"""
def download(pl,url,verbose=False) :
    # Connect to drupal project list url
    r = urllib2.urlopen(url)
    # Get remote drupal project file size
    r_size = r.info().get('Content-Length')
    print 'Remote drupal project list file size is: ' + r_size
    # Get local drupal project file size
    if os.path.exists(pl) :
    	l_size = os.stat(pl)[stat.ST_SIZE]
    	print "Local drupal project list file size is: " + str(l_size)
    else :
        l_size = 0
        print "Local file not existed"    

    if int(l_size) == 0 or int(l_size) != int(r_size) or int(r_size) > int(l_size) :
        print "Downloading: %s Bytes: %s" % (pl, r_size)
        f = open(pl, 'w')
        file_size_dl = 0
        block_sz = 8192
        while True :
            buffer = r.read(block_sz)
            if not buffer :
                break
        
            file_size_dl += block_sz
            f.write(buffer)
            if verbose : 
                status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / int(r_size))
                status = status + chr(8) * (len(status) + 1) + '\r\n'
                print status
        
        f.close()
    else :
        print 'Same size! No need to update project list file.'

def project_checkout(pl,to_path,ptype,noop=False,nofetch=False,verbose=False) :
    if not os.path.exists(to_path):
        os.makedirs(to_path)
        
    with open(pl, 'r') as xml_file:
        parser = etree.XMLParser(encoding='utf-8')
        xml_tree = etree.parse(xml_file)
        elements = xml_tree.findall('./project')
    
    n_projects = len(elements)
    n_projects_loaded = 0
    
    # Total projects
    print "Total number of Drupal projects: " + str(n_projects)
    rex = re.compile('^\d+$')
    
    for element in elements:
        short_name = element.findtext('short_name')
        project_type = element.findtext('type')
        # skip all sandbox projects

        if rex.match(short_name) is not None :
            n_projects_loaded += 1
            if verbose : print "Skip sandbox Project %s" % short_name
            continue
        if (project_type != ('project_%s' % ptype)) :
            n_projects_loaded += 1
            if verbose : print "Skip Project %s (%s)" % (short_name, project_type)
            continue

        title = element.findtext('title')
        path = os.path.join(to_path,short_name)
        
        git_clone_command = "/usr/bin/env git clone git://git.drupal.org/project/" + short_name + ".git " + path
        git_fetch_command = "/usr/bin/env git fetch --all"
        
        if nofetch and (os.path.exists(path)) :
            n_projects_loaded += 1
            if verbose : print "Skip Fetching project: %s" % title
            continue
        if not nofetch and (os.path.exists(path)) :
            args = shlex.split(git_fetch_command)
            if verbose : print "Fetching project: %s" % title 
            #print git_fetch_command
            p = subprocess.Popen(args, cwd=path, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            stdout_value = p.communicate('through stdin to stdout')[0]
            print '\tpass through: %s' % stdout_value
            p.wait()
           #if(p.wait() != None): continue
        else :
            args = shlex.split(git_clone_command)
            if verbose : print "Cloning project: %s" % title
            #print git_clone_command
            p = subprocess.Popen(args, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            stdout_value = p.communicate('through stdin to stdout')[0]
            print '\tpass through: %s' % stdout_value
            p.wait()
            #if(p.wait() != None): continue

#            if GITWEB_ROOT_PATH :
#                # create symlink
#                sl_des = GITWEB_ROOT_PATH + short_name + '.git'
#                sl_src = path + '/.git'
#                if os.path.exists(sl_src):
#                    if not os.path.exists(sl_des):
#                        os.symlink(sl_src, sl_des)
#                    # modify description
#                    f = open(sl_src + '/description', 'w')
#                    f.write(title)
#                    f.close()

        status = r"%10d  [%3.2f%%]" % (n_projects_loaded, n_projects_loaded * 100. / int(n_projects))
        status = status + chr(8) * (len(status) + 1) + '\r\n'
        print status
        
        n_projects_loaded += 1

def main() :
    parser = argparse.ArgumentParser(description='drupal module mirror')
    parser.add_argument('-v', '--verbose', action='store_true', help="Print debus information", default=False)
    parser.add_argument('--noop', action='store_true', help="Do not download anything", default=False)
    parser.add_argument('--nofetch', action='store_true', help="Only clone new projects", default=False)
    parser.add_argument('--type', type=str, help="Download only this project type (default module)", default="module")
    parser.add_argument('targetdir', type=str, nargs=1, help="target directory")
    args = parser.parse_args()

    targetdir = args.targetdir[0]

    if not os.path.exists(targetdir):
        os.makedirs(targetdir)

    listurl = 'http://updates.drupal.org/release-history/project-list/all'
    project_list = os.path.join('/tmp','drupal-project-list-all.xml')
#    if args.ptype == 'drupal' :
#        listurl = 'http://updates.drupal.org/release-history/drupal/all'
#        project_list = os.path.join('/tmp','drupal-core-list-all.xml')

    if not args.noop : 
        download(project_list,listurl,args.verbose)

    project_checkout(project_list,targetdir,args.type,args.noop,args.nofetch,args.verbose)

if __name__ == '__main__':
    main()
