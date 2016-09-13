from fabric.api import env, task, local, run, sudo, parallel
from fabric.operations import put
from fabric.contrib.files import exists, contains, append, sed, upload_template, comment, uncomment
from fabric.utils import error, abort
from fabric.context_managers import cd, settings, hide
from fabric.decorators import hosts
import os, StringIO
from pipes import quote
from crypt import crypt

INSTALL_FILES = './temp_files'
PUBKEY = os.path.join(os.environ['HOME'], '.ssh/id_rsa.pub')

HADOOP_VERSION = '2.7.3'
SPARK_VERSION = '2.0.0'


HADOOP_TARFILE = 'hadoop-%s.tar.gz' % (HADOOP_VERSION,)
HADOOP_APACHE_PATH = '/hadoop/common/hadoop-%s/%s' % (HADOOP_VERSION, HADOOP_TARFILE)
HADOOP_INSTALL = '/opt/hadoop-%s' % (HADOOP_VERSION,)

SPARK_TARFILE = 'spark-%s-bin-hadoop2.6.tgz' % (SPARK_VERSION,)
SPARK_APACHE_PATH = 'spark/spark-%s/%s' % (SPARK_VERSION, SPARK_TARFILE)
SPARK_INSTALL = '/opt/spark-%s-bin-hadoop2.6' % (SPARK_VERSION,)

NUM_SLAVES = 6
SLAVES = ['hadoop%i.local' % (i) for i in range(1, NUM_SLAVES+1)]

HOSTS = ['master.local'] + SLAVES
if not env.hosts:
    env.hosts = HOSTS

env.user = 'pi'
env.skip_bad_hosts = True

def cmd(c, *args):
    """
    Helper to escape command line arguments in a shell command
    """
    return c % tuple(map(quote, args))

def install_file(f):
    """
    Local path for an install file.
    """
    return os.path.join(INSTALL_FILES, f)


@task
def auth_config():
    """
    Set up SSH keys for the pi@ user
    """
    local(cmd('mkdir -p %s', INSTALL_FILES))

    # user SSH key
    if not os.path.isfile(install_file('id_rsa')):
        local(cmd("ssh-keygen -t rsa -b 4096 -N '' -C 'cluster user key' -f %s", install_file('id_rsa')))

    run('mkdir -p -m 0700 .ssh')
    if not exists('.ssh/id_rsa'):
        put(install_file('id_rsa.pub'), '.ssh/id_rsa.pub', mode=0600)
        put(install_file('id_rsa'), '.ssh/id_rsa', mode=0600)

    pubkey = open(install_file('id_rsa.pub'), 'r').read()
    if not contains('.ssh/authorized_keys', pubkey):
        append('.ssh/authorized_keys', pubkey)

    pubkey = open(PUBKEY, 'r').read()
    if not contains('~/.ssh/authorized_keys', pubkey, exact=True):
        append('.ssh/authorized_keys', pubkey)


@task
def clean_raspbian():
    """
    Uninstall stuff we don't need from Raspbian.
    """
    # based on https://gist.github.com/bivald/4182851 and forks
    sudo('apt-get update')
    sudo('''apt-get -y purge xserver* x11-utils x11-xkb-utils x11-xserver-utils xarchiver xauth xkb-data console-setup xinit lightdm \
        obconf openbox alsa* python-pygame python-tk python3-tk scratch tsconf aspell hunspell-en-us iptraf libaspell15 \
        libhunspell-1.2-0 lxde lxsession lxtask lxterminal squeak-vm zenity gdm gnome-themes-standard python-pygame \
        desktop-file-utils omxplayer xserver-xorg ^lx samba-common smbclient cups-bsd cups-client cups-common \
        wolfram-engine cifs-utils samba-common \
        libsysfs2 gstreamer*  libident libboost* libsigc++* x2x fbset libfreetype6-dev libept-dev gtk2-engines gpicview \
        gnome-themes-standard-data gnome-icon-theme galculator python3-picamera  python3-pifacedigital-scratch-handler \
        python3-serial python-picamera python-pifacedigitalio xpdf timidity sonic-pi python3-pifacedigitalio \
        python3-rpi.gpio python-pifacecommon python-rpi.gpio penguinspuzzle v4l-utils xdg-utils minecraft-pi libept1.4.12 \
        smartsim luajit libapt-pkg-dev libtagcoll2-dev libxapian* python3-pifacecommon raspberrypi-artwork libudev0
        ''')
    sudo('apt-get -y autoremove')
    sudo('apt-get -y dist-upgrade')
    sudo('apt-get -y autoclean')
    sudo('apt-get -y clean')
    run('rm -rf /home/pi/python_games')


def _get_apache_file(path, tarfile):
    if not os.path.isfile(install_file(tarfile)):
        local(cmd('%s %s -O %s', install_file('grrrr'), path, install_file(tarfile)))

@task
def fetch_files():
    if not os.path.isdir(INSTALL_FILES):
        local(cmd('mkdir %s', INSTALL_FILES))
    grrrr = install_file('grrrr')
    if not os.path.isfile(grrrr):
        local(cmd('wget --no-check-certificate http://raw.githubusercontent.com/fs111/grrrr/master/grrr -O %s && chmod +x %s', grrrr, grrrr))
    _get_apache_file(HADOOP_APACHE_PATH, HADOOP_TARFILE)
    _get_apache_file(SPARK_APACHE_PATH, SPARK_TARFILE)

@task
def set_hostname():
    try:
        hostname = env['hostname']
    except KeyError:
        error('Must specify --set=hostname=<newhostname> on command line', abort)

    sudo(cmd('echo %s > /etc/hostname', hostname))
    sed('/etc/hosts', '127.0.1.1\s+.*', '127.0.1.1 '+hostname, use_sudo=True)

    # make sure we have a unique SSH signature on this new node
    sudo('rm /etc/ssh/ssh_host_*')
    sudo('dpkg-reconfigure openssh-server')

    sudo('reboot')


def failure(cmd, use_sudo=False, shell=False):
    func = use_sudo and sudo or run
    with settings(hide('everything'), warn_only=True):
        return not func(cmd, shell=shell).succeeded


@task
@parallel
def node_config():
    """
    Basic system setup
    """
    if not exists('/usr/sbin/ntpdate'):
        sudo('apt-get -y install ntpdate')
    if not exists('/usr/bin/sshfs'):
        # handy to copy files onto the cluster
        sudo('apt-get -y install sshfs')

    put('files/interfaces', '/etc/network/interfaces', use_sudo=True)
    upload_template('files/hadoop.sh', '/etc/profile.d/hadoop.sh', context={'hadoop_home': HADOOP_INSTALL}, use_sudo=True)
    run('mkdir -m 0755 -p ~/bin')
    upload_template('files/exec-all.sh', 'bin/exec-all', context={'slaves_list': ' '.join(SLAVES)}, mode=0755)
    if exists('python_games'):
        run('rm -rf python_games')
    if not exists('/usr/share/pam-configs/systemd'):
        sudo('apt-get -y install libpam-systemd')

    # Hadoop user
    if failure('egrep -q "^hadoop:" /etc/passwd'):
        sudo('adduser --system --shell=/bin/bash --home /home/hadoop --group --disabled-password hadoop')
        #sudo('chsh -s /bin/bash hadoop')
    
    sudo('grep -q "^supergroup" /etc/group || groupadd supergroup')
    sudo('usermod -a -G supergroup pi')
    sudo('usermod -a -G supergroup hadoop')

    # mount USB key (formatted "mkfs.ext4 -L HADOOP")
    append('/etc/fstab', 'LABEL=HADOOP /hadoop ext4 defaults,relatime,noauto 0 0', use_sudo=True)
    append('/etc/rc.local', 'mount /hadoop || true', use_sudo=True)
    append('/etc/rc.local', 'chown hadoop:hadoop /hadoop || true', use_sudo=True)
    comment('/etc/rc.local', '^exit 0', use_sudo=True)
    sudo('mkdir -p /hadoop')
    sudo('chown hadoop:hadoop /hadoop')

    # SSH keys
    if not os.path.isfile(install_file('hadoop_id_rsa')):
        local(cmd("ssh-keygen -t rsa -b 4096 -N '' -C 'cluster root key' -f %s", install_file('hadoop_id_rsa')))
    sudo('mkdir -p -m 0700 /home/hadoop/.ssh')
    upload_template('files/ssh-config', '.ssh/config', context={'host_list': ' '.join(HOSTS)}, mode=0600)
    if not exists('/home/hadoop/.ssh/id_rsa'):
        put(install_file('hadoop_id_rsa.pub'), '/home/hadoop/.ssh/id_rsa.pub', mode=0644, use_sudo=True)
        put(install_file('hadoop_id_rsa.pub'), '/home/hadoop/.ssh/authorized_keys', mode=0644, use_sudo=True)
        put(install_file('hadoop_id_rsa'), '/home/hadoop/.ssh/id_rsa', mode=0600, use_sudo=True)

    sudo('chown -R hadoop:hadoop /home/hadoop/.ssh')

    # /etc/hosts dynamic reconfig (needed by zookeeper)
    if not exists('/etc/hosts.template'):
        sudo('(grep -v 127.0.1.1 /etc/hosts | grep -v "# auto"; echo "HOST # auto") > /etc/hosts.template')
    put('files/update-hosts.sh', '/etc/network/if-up.d/update-hosts.sh', mode=0755, use_sudo=True)
    
    # Java
    if not exists('/usr/bin/java'):
        sudo('apt-get -y install openjdk-8-jre')



ssh_keys_cache = None
def collect_ssh_keys():
    global ssh_keys_cache
    if ssh_keys_cache:
        return ssh_keys_cache

    ssh_keys = []
    for h in HOSTS:
        with settings(warn_only=True):
            key = local(cmd('ssh-keyscan %s', h), capture=True)
        if key:
            ssh_keys.append(key)

    ssh_keys_cache = '\n'.join(ssh_keys)
    return ssh_keys_cache + '\n'

@task
def ssh_keyscan():
    ssh_keys = collect_ssh_keys()
    keydata = StringIO.StringIO(ssh_keys)
    put(keydata, '/home/hadoop/.ssh/known_hosts', use_sudo=True)
    sudo('chown hadoop.hadoop /home/hadoop/.ssh/known_hosts')

    run('mkdir -p .ssh && chmod 0700 .ssh')
    put(keydata, '.ssh/known_hosts')



@task
@parallel
def install_hadoop():
    # Hadoop
    sudo('mkdir -p /opt')
    if not exists(os.path.join(HADOOP_INSTALL, 'bin/hadoop')):
        put(install_file(HADOOP_TARFILE), os.path.join('/opt', HADOOP_TARFILE), use_sudo=True)
        with cd('/opt'):
            sudo(cmd('tar zxf %s', HADOOP_TARFILE))
        sudo(cmd('rm %s', os.path.join('/opt', HADOOP_TARFILE)))
        sudo(cmd('chown -R hadoop.hadoop %s', HADOOP_INSTALL))

    # Hadoop config files
    put('files/core-site.xml', '%s/etc/hadoop/core-site.xml' % (HADOOP_INSTALL,), use_sudo=True)
    put('files/hdfs-site.xml', '%s/etc/hadoop/hdfs-site.xml' % (HADOOP_INSTALL,), use_sudo=True)
    put('files/yarn-site.xml', '%s/etc/hadoop/yarn-site.xml' % (HADOOP_INSTALL,), use_sudo=True)
    put('files/mapred-site.xml', '%s/etc/hadoop/mapred-site.xml' % (HADOOP_INSTALL,), use_sudo=True)
    put('files/masters', '%s/etc/hadoop/masters' % (HADOOP_INSTALL,), use_sudo=True)
    upload_template('files/slaves', '%s/etc/hadoop/slaves' % (HADOOP_INSTALL,), context={'slaves_list': '\n'.join(SLAVES)}, use_sudo=True)

    hadoop_env = '%s/etc/hadoop/hadoop-env.sh' % (HADOOP_INSTALL,)
    sed(hadoop_env, '^export JAVA_HOME=.*', 'export JAVA_HOME=$(readlink -f /usr/bin/java | sed "s:bin/java::")', use_sudo=True)
    uncomment(hadoop_env, 'export\s+HADOOP_HEAPSIZE=', use_sudo=True)
    sed(hadoop_env, '^export\s+HADOOP_HEAPSIZE=.*', 'export HADOOP_HEAPSIZE=256', use_sudo=True)
    if not contains(hadoop_env, '^export HADOOP_DATANODE_OPTS=.*-client', escape=False, use_sudo=True):
        sed(hadoop_env, '^export HADOOP_DATANODE_OPTS="(.*)"$', 'export HADOOP_DATANODE_OPTS="\\1 -client"', use_sudo=True)

    sudo(cmd('ln -sf %s /opt/hadoop', HADOOP_INSTALL))
    for f in ['start-all.sh', 'stop-all.sh', 'dfs-format.sh', 'clear-dfs.sh', 'nuke-dfs.sh', 'halt-all.sh', 'hdfs-balance.sh']:
        put('files/' + f, 'bin/' + f.replace('.sh', ''), mode=0755)

    # HDFS directories
    sudo('mkdir -p -m 0750 /hadoop/tmp && chown hadoop:hadoop /hadoop/tmp')
    sudo('mkdir -p /hadoop/namenode && chown hadoop:hadoop /hadoop/namenode')
    sudo('mkdir -p /hadoop/datanode && chown hadoop:hadoop /hadoop/datanode')

@task
@hosts('master.local')
def install_spark():
    """
    Install Spark on the master node
    """
    if not exists(os.path.join(SPARK_INSTALL, 'bin/spark-submit')):
        put(install_file(SPARK_TARFILE), os.path.join('/opt', SPARK_TARFILE), use_sudo=True)
        with cd('/opt'):
            sudo(cmd('tar zxf %s', SPARK_TARFILE))
        sudo(cmd('rm %s', os.path.join('/opt', SPARK_TARFILE)))
        sudo(cmd('chown -R hadoop.hadoop %s', SPARK_INSTALL))

    sudo(cmd('ln -sf %s /opt/spark', SPARK_INSTALL))
    put('files/spark-defaults.conf', '%s/conf/spark-defaults.conf' % (SPARK_INSTALL,), use_sudo=True)

@task
@hosts('master.local')
def course_prep():
    """
    Prep specific to SFU CMPT 732
    """
    put('files/Makefile', 'Makefile')


@task
@parallel
def change_password():
    """
    Change the password on the pi@ accounts
    """
    try:
        passwd = env['passwd']
    except KeyError:
        error('Must specify --set=passwd="<newpasswd>" on command line', abort)

    cpw = crypt(passwd, 'mmmsalt')
    sudo(cmd('usermod --password %s pi', cpw))


@task
def send_cmd():
    try:
        cmd = env['cmd']
    except KeyError:
        error('Must specify --set=cmd="the_command to run" on command line', abort)

    with settings(warn_only=True):
        sudo(cmd)
