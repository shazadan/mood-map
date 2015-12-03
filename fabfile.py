from fabric.api import env, local, run, sudo, require

APT_INSTALL_PACKAGES = [
                        "libpq-dev",
                        "python-dev",
                        "libffi-dev",
                        "libssl-dev",
                        "python-pip",
                        "postgresql",
                        "postgresql-contrib",
                        "redis-server",
                        "supervisor"
                        ]

base = '/server'
virtualenvs = '.virtualenvs'
projects = 'projects'
repo = 'mood-map'

# Environments
def vagrant():
    # change from the default user to 'vagrant'
    env.user = 'vagrant'
    # connect to the port-forwarded ssh
    env.hosts = ['127.0.0.1:2222']
    # use vagrant ssh key
    result = local('vagrant ssh-config | grep IdentityFile', capture=True)
    env.key_filename = result.split()[1]
    env.base_dir = base
    env.virtualenvs_dir = virtualenvs
    env.virtualenv = '01'
    env.projects_dir = projects
    env.repo_dir = repo
    env.settings = 'local'

# Bootstrap commands
def bootstrap():
    require('hosts',  provided_by=[vagrant])
    bs_install_packages()
    bs_make_folder_structure()
    bs_setup_virtualenv()
    bs_link_project()
    bs_install_requirements()
    bs_install_heroku_toolbelt()
    bs_setup_supervisor()

def bs_install_packages():
    sudo("apt-get update")
    sudo("apt-get upgrade -y")
    sudo("apt-get -y install " + " ".join(APT_INSTALL_PACKAGES))

def bs_make_folder_structure():
    sudo("if [ ! -d %(base_dir)s ]; then mkdir -p %(base_dir)s; chmod 777 "
          "%(base_dir)s; fi" % env)
    sudo("if [ ! -d %(base_dir)s/%(virtualenvs_dir)s ]; then mkdir -p %("
          "base_dir)s/%("
         "virtualenvs_dir)s; chmod "
         "777 %(base_dir)s/%(virtualenvs_dir)s; fi" % env)
    sudo("if [ ! -d %(base_dir)s/%(projects_dir)s ]; then mkdir -p %("
          "base_dir)s/%("
         "projects_dir)s; chmod "
         "777 %(base_dir)s/%(projects_dir)s; fi" % env)

    #setup logging folder
    sudo("if [ ! -d %(base_dir)s/%(projects_dir)s/logs ]; then mkdir -p %("
          "base_dir)s/%("
         "projects_dir)s/logs/%(repo_dir)s; chmod "
         "777 %(base_dir)s/%(projects_dir)s/logs/%(repo_dir)s; fi" % env)

def bs_setup_virtualenv():
    "Fetches the virtualenv package"
    run("if [ ! -e virtualenv-13.1.0.tar.gz ]; then wget "
        " https://pypi.python.org/packages/source/v/virtualenv/virtualenv-13"
        ".1.0.tar.gz; fi")
    run("if [ ! -d virtualenv-13.1.0 ]; then tar xzf "
         "virtualenv-13.1.0.tar.gz; fi")
    run("rm -f virtualenv")
    run("ln -s virtualenv-13.1.0 virtualenv")
    run("if [ ! -d %(base_dir)s/%(virtualenvs_dir)s/%(virtualenv)s ]; then "
         "python "
        "~/virtualenv/virtualenv.py --no-site-packages %(base_dir)s/%("
        "virtualenvs_dir)s/%(virtualenv)s; fi" % env)
    sudo("chmod 777 %(base_dir)s/%(virtualenvs_dir)s/%(virtualenv)s" % env)

def bs_link_project(): # vagrant only
    run("ln -s /vagrant %(base_dir)s/%(projects_dir)s/%(repo_dir)s" % env)

def bs_install_requirements():
    sudo("source %(base_dir)s/%(virtualenvs_dir)s/%(virtualenv)s/bin/activate;"
         "pip install -r %(base_dir)s/%(projects_dir)s/%("
         "repo_dir)s/requirements/%(settings)s.txt;" % env)

def bs_install_heroku_toolbelt():
    run("wget -O- https://toolbelt.heroku.com/install-ubuntu.sh | sh")

def bs_setup_supervisor():
    run('touch %(base_dir)s/%(projects_dir)s/logs/%('
         'repo_dir)s/celery-worker.log' % env)
    sudo('cp %(base_dir)s/%(projects_dir)s/%('
         'repo_dir)s/config/supervisor/mood-map-celery.conf '
         '/etc/supervisor/conf.d/mood-map-celery.conf' % env)
    sudo('supervisorctl reread')
    sudo('supervisorctl update')


# Django commands
def runserver():
    run("source %(base_dir)s/%(virtualenvs_dir)s/%("
        "virtualenv)s/bin/activate; python %("
        "base_dir)s/%(projects_dir)s/%(repo_dir)s/manage.py "
        "runserver "
        "0.0.0.0:8000 --settings=config.settings.%(settings)s" % env)

def migrate():
    run("source %(base_dir)s/%(virtualenvs_dir)s/%("
        "virtualenv)s/bin/activate; python %("
        "base_dir)s/%(projects_dir)s/%(repo_dir)s/manage.py "
        "migrate --settings=config.settings.%(settings)s" % env)

def collectstatic():
    run("source %(base_dir)s/%(virtualenvs_dir)s/%("
        "virtualenv)s/bin/activate; python %("
        "base_dir)s/%(projects_dir)s/%(repo_dir)s/manage.py "
        "collectstatic --settings=config.settings.%(settings)s" % env)

def test():
    run("source %(base_dir)s/%(virtualenvs_dir)s/%("
        "virtualenv)s/bin/activate; coverage run %("
        "base_dir)s/%(projects_dir)s/%(repo_dir)s/manage.py "
        "test "
        "--settings=config.settings.%(settings)s" % env)

def test_report():
    run("source %(base_dir)s/%(virtualenvs_dir)s/%(virtualenv)s/bin/activate;"
        "cd %(base_dir)s/%(projects_dir)s//%(repo_dir)s/;"
        "coverage html --omit='admin.py'" % env)

# Supervisor commands
def supervisor_status():
    sudo('supervisorctl status')
