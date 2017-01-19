import jinja2
import os

import charmhelpers.core.hookenv as hookenv
import charmhelpers.core.host as host
import charmhelpers.core.templating as ch_templating
import shutil
import subprocess

FLASK_SERVICE="flask-server"
FLASK_ASSETS = {
     'STATIC_FILES': ['/etc/systemd/system/flask-server.service', '/opt/flask_slave/flask_server.py'],
     'TEMPLATES': ['/opt/flask_slave/conf/flask_config.cfg', '/opt/flask_slave/static/index.html']}

def log(msg):
    print(msg)

def setup_dirs():
    for fdir in FLASK_ASSETS['STATIC_FILES'] + FLASK_ASSETS['TEMPLATES']:
        base_dir = os.path.dirname(fdir)
        if not os.path.exists(base_dir):
            log("Creating {}".format(base_dir))
            os.makedirs(base_dir)

def copy_static_files():
    src_file_dir = os.path.join(hookenv.charm_dir(), 'files')
    for tfile in FLASK_ASSETS['STATIC_FILES']:
        log("Copying over {}".format(tfile))
        shutil.copy2(os.path.join(src_file_dir, os.path.basename(tfile)),
                     tfile)

def charm_context():
    there_must_be_a_more_idiomatic_way = {}
    for key, value in hookenv.config().items():
        there_must_be_a_more_idiomatic_way[key.replace('-', '_')] = value
    return there_must_be_a_more_idiomatic_way

def render_files():
    template_path = os.path.join(hookenv.charm_dir(), 'templates')
    fs_loader = jinja2.FileSystemLoader(template_path)
    templateEnv = jinja2.Environment( loader=fs_loader )
    for tfile in FLASK_ASSETS['TEMPLATES']:
        log("Rendering over {}".format(tfile))
        template = templateEnv.get_template(os.path.basename(tfile))
        with open(tfile, 'w') as target:
            target.write(template.render(charm_context()))
    
def reload_systemd():
    log("Reloading systemd def")
    subprocess.check_call(['systemctl', 'daemon-reload'])

def setup_flask():
    setup_dirs()
    copy_static_files()
    render_files()
    host.service_restart(FLASK_SERVICE)
