import sys, os, time, re, pickle
from fabric.state import env
from fabric.decorators import task, parallel
from fabric.operations import put, run, sudo
from fabric.context_managers import cd, hide, settings
from fabric.contrib.files import exists

here = os.path.abspath(os.path.dirname(__file__))

def _median(numbers):
    numbers = sorted(numbers)
    size = len(numbers)
    if size % 2:
        return int(round(numbers[(size - 1) / 2]))
    else:
        return int(round((numbers[size/2 - 1] + numbers[size/2]) / 2))

def _average(numbers):
    return int(round(sum(numbers, 0.0) / len(numbers)))


@task
@parallel
def mod_wsgi(run_tests=True):
    """Run the Python mod_wsgi control test."""
    INSTALL = 'apache2-mpm-worker libapache2-mod-wsgi curl'
    TEST_URL = 'http://localhost/'
    
    # Check the correct usage
    if not re.match(r'^test:?', sys.argv[1]):
        print '\nERROR: You must run "test" as the first task. Run "fab -l" ' \
              'for more information and a complete list of tasks.\n'
        sys.exit(1)
    
    # Get current instance info
    for instance in env.instances:
        if instance.public_dns_name == env.host:
            break
    
    with settings(hide('running', 'stdout')):
        if exists('/etc/apache2/mods-available/wsgi.load') and \
           exists('/usr/sbin/apache2ctl') and \
           sudo('apache2ctl -V | '
                'grep -m 1 "Server MPM"').strip().endswith('Worker'):
            sudo('a2enmod wsgi')
        else:
            # Do installs
            sudo('apt-get update')
            sudo('apt-get -y install ' + INSTALL)
            sudo('a2enmod wsgi')
        
        if run_tests is False or run_tests == 'False':
            return
        
        # Setup test environment
        sudo('a2dissite 000-default')
        put(os.path.join(here, 'vhost.conf'),
            '/etc/apache2/sites-enabled/', use_sudo=True)
        put(here, '/var/www/', use_sudo=True)
        # For good measure
        sudo('chmod -R 777 /var/www/python/')
        sudo('/etc/init.d/apache2 restart', pty=False)
        time.sleep(1)
    
        # Check the test url
        if run('curl %s' % TEST_URL) != "Hello World!":
            print '*' * 80
            print '*%s*' % 'INVALID WEBSERVER RESPONSE'.center(78)
            print '*' * 80
            
            raise
        
        # Run ab
        output = ''
        for i in range(env.NUM_AB_TESTS):
            output += run(
                'ab %s %s | egrep "(^Failed)|(^Non-2xx)|(^Requests)"' %
                (env.AB_FLAGS, TEST_URL)
                )
            output += '\n'
            time.sleep(1)
    
        # Disable module
        sudo('a2dismod wsgi')
    
    output = output.strip().split('\n')
    for line in output:
        if (line.startswith('Failed requests') or \
            line.startswith('Non-2xx responses')) and \
           not line.strip().endswith('0'):
            print '*' * 80
            print '*%s*' % 'INVALID APACHEBENCH RESPONSE'.center(78)
            print '*' * 80
            print line
            
            raise
        elif line.startswith('Requests per second'):
            env.results['hello'].append(float(re.sub('[^0-9.]', '', line)))
    
    # Get the median of all results
    result = _median(env.results['hello'])
    
    # Update the results file
    env.resultsfp.seek(0)
    results_data = pickle.loads(env.resultsfp.read())
    
    if env.command not in results_data:
        results_data[env.command] = dict()
    if instance.id not in results_data[env.command]:
        results_data[env.command][instance.id] = dict()
    
    results_data[env.command][instance.id]['hello'] = result
    results_data[env.command][instance.id]['tmpl'] = 'n/a'
    results_data[env.command][instance.id]['db'] = 'n/a'
    env.resultsfp.seek(0)
    env.resultsfp.write(pickle.dumps(results_data))
    env.resultsfp.truncate()


@task
@parallel
def uwsgi(run_tests=True):
    """Run the Python uWSGI server control test."""
    INSTALL = 'build-essential apache2-utils dtach python-dev python-pip ' \
              'libxml2-dev curl'
    TEST_URL = 'http://localhost:9090/'
    
    # Check the correct usage
    if not re.match(r'^test:?', sys.argv[1]):
        print '\nERROR: You must run "test" as the first task. Run "fab -l" ' \
              'for more information and a complete list of tasks.\n'
        sys.exit(1)
    
    # Get current instance info
    for instance in env.instances:
        if instance.public_dns_name == env.host:
            break
    
    with settings(hide('running', 'stdout')):
        if exists('/usr/sbin/ab') and exists('/usr/bin/pip') and \
           exists('/usr/local/bin/uwsgi') and exists('/usr/bin/dtach'):
            # Kill uWSGI before running it again
            if int(run('ps aux | grep -c uwsgi')) > 2:
                sudo('killall -9 uwsgi')
        else:
            # Do installs
            sudo('apt-get update')
            sudo('apt-get -y install ' + INSTALL)
            sudo('pip install uwsgi==1.0.4')
    
        # Setup test environment
        put(here, '/home/ubuntu/', use_sudo=True)
        # For good measure
        sudo('chmod -R 777 /home/ubuntu/python/')
        run('dtach -n /tmp/uwsgi -Ez uwsgi -L --http :9090 --wsgi-file '
            '/home/ubuntu/python/python.wsgi')
        time.sleep(1)
        
        if run_tests is False or run_tests == 'False':
            return
        
        # Check the test url
        if run('curl %s' % TEST_URL) != "Hello World!":
            print '*' * 80
            print '*%s*' % 'INVALID WEBSERVER RESPONSE'.center(78)
            print '*' * 80
            
            raise
        
        # Run ab
        output = ''
        for i in range(env.NUM_AB_TESTS):
            output += run(
                'ab %s %s | egrep "(^Failed)|(^Non-2xx)|(^Requests)"' %
                (env.AB_FLAGS, TEST_URL)
                )
            output += '\n'
            time.sleep(1)
        
        # Terminate instance
        sudo('killall -9 uwsgi')
    
    output = output.strip().split('\n')
    for line in output:
        if (line.startswith('Failed requests') or \
            line.startswith('Non-2xx responses')) and \
           not line.strip().endswith('0'):
            print '*' * 80
            print '*%s*' % 'INVALID APACHEBENCH RESPONSE'.center(78)
            print '*' * 80
            print line
            
            raise
        elif line.startswith('Requests per second'):
            env.results['hello'].append(float(re.sub('[^0-9.]', '', line)))
    
    # Get the median of all results
    result = _median(env.results['hello'])
    
    # Update the results file
    env.resultsfp.seek(0)
    results_data = pickle.loads(env.resultsfp.read())
    
    if env.command not in results_data:
        results_data[env.command] = dict()
    if instance.id not in results_data[env.command]:
        results_data[env.command][instance.id] = dict()
    
    results_data[env.command][instance.id]['hello'] = result
    results_data[env.command][instance.id]['tmpl'] = 'n/a'
    results_data[env.command][instance.id]['db'] = 'n/a'
    env.resultsfp.seek(0)
    env.resultsfp.write(pickle.dumps(results_data))
    env.resultsfp.truncate()


@task
@parallel
def gunicorn(run_tests=True):
    """Run the Python Gunicorn (sync) server control test."""
    INSTALL = 'build-essential apache2-utils dtach python-dev python-pip ' \
              'libxml2-dev curl'
    TEST_URL = 'http://localhost:8000/'
    
    # Check the correct usage
    if not re.match(r'^test:?', sys.argv[1]):
        print '\nERROR: You must run "test" as the first task. Run "fab -l" ' \
              'for more information and a complete list of tasks.\n'
        sys.exit(1)
    
    # Get current instance info
    for instance in env.instances:
        if instance.public_dns_name == env.host:
            break
    
    with settings(hide('running', 'stdout')):
        if exists('/usr/sbin/ab') and exists('/usr/bin/pip') and \
           exists('/usr/local/bin/gunicorn') and exists('/usr/bin/dtach'):
            # Kill Gunicorn before running it again
            if int(run('ps aux | grep -c gunicorn')) > 2:
                sudo('killall -9 gunicorn')
        else:
            # Do installs
            sudo('apt-get update')
            sudo('apt-get -y install ' + INSTALL)
            sudo('pip install gunicorn==0.14.1')
    
        # Setup test environment
        put(here, '/home/ubuntu/', use_sudo=True)
        # For good measure
        sudo('chmod -R 777 /home/ubuntu/python/')
        with cd('/home/ubuntu/python/'):
            run('dtach -n /tmp/gunicorn -Ez gunicorn -w 5 python:application')
        time.sleep(1)
        
        if run_tests is False or run_tests == 'False':
            return
        
        # Check the test url
        if run('curl %s' % TEST_URL) != "Hello World!":
            print '*' * 80
            print '*%s*' % 'INVALID WEBSERVER RESPONSE'.center(78)
            print '*' * 80
            
            raise
        
        # Run ab
        output = ''
        for i in range(env.NUM_AB_TESTS):
            output += run(
                'ab %s %s | egrep "(^Failed)|(^Non-2xx)|(^Requests)"' %
                (env.AB_FLAGS, TEST_URL)
                )
            output += '\n'
            time.sleep(1)
        
        # Terminate instance
        sudo('killall -9 gunicorn')
    
    output = output.strip().split('\n')
    for line in output:
        if (line.startswith('Failed requests') or \
            line.startswith('Non-2xx responses')) and \
           not line.strip().endswith('0'):
            print '*' * 80
            print '*%s*' % 'INVALID APACHEBENCH RESPONSE'.center(78)
            print '*' * 80
            print line
            
            raise
        elif line.startswith('Requests per second'):
            env.results['hello'].append(float(re.sub('[^0-9.]', '', line)))
    
    # Get the median of all results
    result = _median(env.results['hello'])
    
    # Update the results file
    env.resultsfp.seek(0)
    results_data = pickle.loads(env.resultsfp.read())
    
    if env.command not in results_data:
        results_data[env.command] = dict()
    if instance.id not in results_data[env.command]:
        results_data[env.command][instance.id] = dict()
    
    results_data[env.command][instance.id]['hello'] = result
    results_data[env.command][instance.id]['tmpl'] = 'n/a'
    results_data[env.command][instance.id]['db'] = 'n/a'
    env.resultsfp.seek(0)
    env.resultsfp.write(pickle.dumps(results_data))
    env.resultsfp.truncate()
