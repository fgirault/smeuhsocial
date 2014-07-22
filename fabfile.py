from __future__ import with_statement
import os
from datetime import datetime
from fabric.api import env, run, prefix, local, cd, roles, settings
from fabric.api import get

try:
    import local_settings
except ImportError:
    import settings as local_settings


DATETIME_FMT = "%Y-%m-%d_%H-%M"
PROJECT_DIR = os.path.dirname(__file__)

env.roledefs = {
    'smeuh': ['smeuhsocial@smeuh.org:2224'],
}

env.use_ssh_config = True


def push():
    local('git push')


def deploy():
    push()
    with cd("smeuhsocial"):
        run("git pull")
        with prefix("source ~/.virtualenvs/smeuhsocial/bin/activate"):
            run("pip install -r requirements.txt")
            run("./manage.py collectstatic --noinput")
        run("touch deploy/pinax.wsgi")


@roles('smeuh')
def make_remote_backup_dir():
    remote_dir = "/home/smeuhsocial/backup"
    with settings(warn_only=True):
        if run("test -d %s" % remote_dir).failed:
            run("mkdir %s" % remote_dir)
    return remote_dir


def backup_db(kwargs):
    local_dir = os.path.join(PROJECT_DIR, "backup")
    kwargs['backup_file'] = ("smeuhsocial_%s.sql" %
                             datetime.now().strftime(DATETIME_FMT))
    kwargs['archive_file'] = ("%(backup_file)s.gz" % kwargs)
    with prefix("export PGPASSWORD={PASSWORD}".format(**kwargs)):
        cmd_tmpl = 'pg_dump -c -h {HOST} -U {USER} {NAME} > {backup_file}'
        run(cmd_tmpl.format(**kwargs))
    run("gzip {backup_file}".format(**kwargs))
    local_path = os.path.join(local_dir,
                              kwargs['archive_file'])
    get(kwargs['archive_file'], local_path)


def backup_media():
    host, port = env.host_string.split(':')
    local("rsync --port={port} -av {host}:site_media .".format(
          host=host, port=port))


@roles('smeuh')
def backup():
    remote_dir = make_remote_backup_dir()
    with cd(remote_dir):
        db_settings = local_settings.DATABASES['default']
        backup_db(db_settings)
    backup_media()


def createdb():
    kwargs = local_settings.DATABASES['default']
    sql = "create user {USER} with password '{PASSWORD}'"
    local('sudo -u postgres psql -c "%s"' % sql.format(**kwargs))
    local('sudo -u postgres createdb --owner {USER} {NAME}'.format(**kwargs))


def restore(archive):
    kwargs = local_settings.DATABASES['default']
    kwargs['archive'] = archive
    kwargs['sql_dump'] = archive.replace('.gz', '')
    local('gzip -cd {archive} > {sql_dump}'.format(**kwargs))
    with prefix("export PGPASSWORD=%s" % kwargs['PASSWORD']):
        local('psql -h {HOST} -U {USER} {NAME} < {sql_dump}'.format(**kwargs))
