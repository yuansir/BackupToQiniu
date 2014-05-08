#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import sys
from time import strftime,gmtime
import tarfile
import qiniu.conf
import qiniu.io
import qiniu.rs

qiniu.conf.ACCESS_KEY = "xxxxxxxxxxxxxxxxxxx"
qiniu.conf.SECRET_KEY = "xxxxxxxxxxxxxxxxxxx"
bucket_name = 'website-backup'
db_host = '127.0.0.1'
db_user = 'root'
db_password = 'xxxxxxxxxxxxx'
db_name = 'xxxxxxxxxxxxx'
db_charset = 'utf8'
file_name = strftime("%Y-%m-%d",gmtime())
back_dir = '/www/backup/'
web_root = '/www/web/yuansirweb/public_html/'
tar_file = back_dir.rstrip('/')+'/'+file_name+'.tar.gz'
db_file = back_dir.rstrip('/')+'/'+'db.sql'

def log(status='Success',content=''):
	print '%s [%s] %s' %(strftime("%Y/%m/%d %H:%M:%S",gmtime()),status,content)

tar = tarfile.open(tar_file,'w|gz')
for root,dirs,files in os.walk(web_root):
	for file in files:
		tar.add(os.path.join(root,file))

sql_dump = os.system("mysqldump -h%s -u%s -p%s %s --default_character-set=%s > %s" \
	%(db_host, db_user, db_password, db_name, db_charset, db_file))

if sql_dump == 0:
	tar.add(db_file)
else:
	log('Error','db dump fail')

tar.close()
if os.path.exists(back_dir+file_name+'.tar.gz') != True:
	log('Error','tar fail')
	sys.exit()

policy = qiniu.rs.PutPolicy(bucket_name)
uptoken = policy.token()
ret, err = qiniu.io.put_file(uptoken, file_name+'.tar.gz',tar_file)
if err is not None:
	log('Error',err)
else:
	log('Success','Back Up Success')

os.remove(db_file)
os.remove(tar_file)