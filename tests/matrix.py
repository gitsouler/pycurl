import os.path, urllib, subprocess, shutil

python_versions = ['2.4.6', '2.5.6', '2.6.8', '2.7.5']
libcurl_versions = ['7.19.0', '7.32.0']

class in_dir:
    def __init__(self, dir):
        self.dir = dir
    
    def __enter__(self):
        self.oldwd = os.getcwd()
        os.chdir(self.dir)
    
    def __exit__(self, type, value, traceback):
        os.chdir(self.oldwd)

def fetch(url, archive):
    if not os.path.exists(archive):
        print "Fetching %s" % url
        io = urllib.urlopen(url)
        with open('.tmp.%s' % archive, 'w') as f:
            while True:
                chunk = io.read(65536)
                if len(chunk) == 0:
                    break
                f.write(chunk)
        os.rename('.tmp.%s' % archive, archive)

def build(archive, dir, prefix):
    if not os.path.exists(dir):
        print "Building %s" % archive
        subprocess.check_call(['tar', 'xf', archive])
        with in_dir(dir):
            subprocess.check_call(['./configure', '--prefix=%s' % prefix])
            subprocess.check_call(['make'])
            subprocess.check_call(['make', 'install'])

for python_version in python_versions:
    url = 'http://www.python.org/ftp/python/%s/Python-%s.tgz' % (python_version, python_version)
    archive = os.path.basename(url)
    fetch(url, archive)
    
    dir = archive.replace('.tgz', '')
    prefix = os.path.abspath('i/%s' % dir)
    build(archive, dir, prefix)

for libcurl_version in libcurl_versions:
    url = 'http://curl.haxx.se/download/curl-%s.tar.gz' % libcurl_version
    archive = os.path.basename(url)
    fetch(url, archive)
    
    dir = archive.replace('.tar.gz', '')
    prefix = os.path.abspath('i/%s' % dir)
    build(archive, dir, prefix)

fetch('https://raw.github.com/pypa/virtualenv/1.7/virtualenv.py', 'virtualenv-1.7.py')

if not os.path.exists('venv'):
    os.mkdir('venv')

for python_version in python_versions:
    for libcurl_version in libcurl_versions:
        python_prefix = os.path.abspath('i/Python-%s' % python_version)
        libcurl_prefix = os.path.abspath('i/curl-%s' % libcurl_version)
        venv = os.path.abspath('venv/Python-%s-curl-%s' % (python_version, libcurl_version))
        if os.path.exists(venv):
            shutil.rmtree(venv)
        subprocess.check_call(['python', 'virtualenv-1.7.py', venv, '-p', '%s/bin/python' % python_prefix])
        with in_dir('pycurl'):
            subprocess.check_call('make clean && . %s/bin/activate && make test' % venv, shell=True)
