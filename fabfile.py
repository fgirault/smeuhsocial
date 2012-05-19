from __future__ import with_statement
from fabric.api import env, run, prefix, local, cd

env.use_ssh_config = True

def push():
    local('git push')


def deploy():
    push()
    with cd("smeuhsocial"):
        run("git pull")
        with prefix("source ~/env/bin/activate"):
            run("pip install -r requirements/project.txt")
            run("./manage.py collectstatic --noinput")
        run("touch deploy/pinax.wsgi")
