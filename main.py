#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
from time import strftime, gmtime
import tarfile
import qiniu
from settings import auth, database, common

tar_name = strftime("%Y-%m-%d", gmtime()) + '.tar.gz'
tar_file = common.TMP_BACK_DIR + '/' + tar_name
tar = tarfile.open(tar_file, 'w|gz')


def log(status='Success', content=''):
    print '%s [%s] %s' % (strftime("%Y/%m/%d %H:%M:%S", gmtime()), status, content)


def tarFiles():
    for root, dirs, files in os.walk(common.WET_ROOT):
        for file in files:
            tar.add(os.path.join(root, file))


def tarDbs():
    for db_name in database.DB_NAMES:
        db_file = common.TMP_BACK_DIR + '/' + db_name + '.sql'
        sql_dump = os.system("%s -h%s -u%s -p%s %s --default_character-set=%s > %s" % (
            common.MYSQL_DUMP_BIN, database.DB_HOST, database.DB_USER, database.DB_PASSOWRD, db_name, 'utf8', db_file))

        if sql_dump == 0:
            tar.add(db_file)
            os.remove(db_file)
        else:
            log('Error', 'database `%s` dump fail' % db_name)

    tar.close()


def upToQiniu():
    upload_file = tar_file
    if os.path.exists(upload_file) != True:
        log('Error', 'tar fail')
        sys.exit()

    q = qiniu.Auth(auth.ACCESS_KEY, auth.SECRET_KEY)
    uptoken = q.upload_token(common.BUCKET_NAME, tar_name)
    ret, info = qiniu.put_file(uptoken, tar_name, upload_file)

    if info.exception == None and info.status_code == 200:
        os.remove(upload_file)
    else:
        log('Error', 'qiniu upload fail')


if __name__ == '__main__':
    tarFiles()
    tarDbs()
    upToQiniu()

