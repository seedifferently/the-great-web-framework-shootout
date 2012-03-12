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
def mod_wsgi():
    """Run the Flask mod_wsgi test."""
    INSTALL = 'build-essential apache2-utils apache2-mpm-worker python-dev ' \
              'python-pip libapache2-mod-wsgi curl'
    HELLO_TEST_URL = 'http://localhost/'
    TMPL_TEST_URL = 'http://localhost/jinja_hello'
    DB_TEST_URL = 'http://localhost/jinja_sql'
    
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
           exists('/usr/local/lib/python2.6/dist-packages/flask/') and \
           exists('/usr/bin/pip') and exists('/usr/sbin/apache2ctl') and \
           sudo('apache2ctl -V | '
                'grep -m 1 "Server MPM"').strip().endswith('Worker'):
            sudo('a2enmod wsgi')
        else:
            # Do installs
            sudo('apt-get update')
            sudo('apt-get -y install ' + INSTALL)
            sudo('pip install flask==0.8')
            sudo('a2enmod wsgi')
    
        # Setup test environment
        sudo('a2dissite 000-default')
        put(os.path.join(here, 'vhost.conf'),
            '/etc/apache2/sites-enabled/', use_sudo=True)
        put(here, '/var/www/', use_sudo=True)
        sudo('rm /var/www/flask/__init__.*')
        # For good measure
        sudo('chmod -R 777 /var/www/flask/')
        sudo('/etc/init.d/apache2 restart', pty=False)
        time.sleep(1)
    
        # Check the test urls
        if run('curl %s' % HELLO_TEST_URL) != "Hello World!":
            print '*' * 80
            print '*%s*' % 'INVALID WEBSERVER RESPONSE'.center(78)
            print '*' * 80
            
            raise
        elif 'Lorem ipsum' not in run('curl %s' % TMPL_TEST_URL):
            print '*' * 80
            print '*%s*' % 'INVALID WEBSERVER RESPONSE'.center(78)
            print '*' * 80
            
            raise
        elif '1</td><td>Lorem' not in run('curl %s' % DB_TEST_URL):
            print '*' * 80
            print '*%s*' % 'INVALID WEBSERVER RESPONSE'.center(78)
            print '*' * 80
            
            raise
        
        # Run ab
        output = dict(hello='', tmpl='', db='')
        for i in range(env.NUM_AB_TESTS):
            output['hello'] += run(
                'ab %s %s | egrep "(^Failed)|(^Non-2xx)|(^Requests)"' %
                (env.AB_FLAGS, HELLO_TEST_URL)
                )
            output['hello'] += '\n'
            time.sleep(1)
        
        for i in range(env.NUM_AB_TESTS):
            output['tmpl'] += run(
                'ab %s %s | egrep "(^Failed)|(^Non-2xx)|(^Requests)"' %
                (env.AB_FLAGS, TMPL_TEST_URL)
                )
            output['tmpl'] += '\n'
            time.sleep(1)
        
        for i in range(env.NUM_AB_TESTS):
            output['db'] += run(
                'ab %s %s | egrep "(^Failed)|(^Non-2xx)|(^Requests)"' %
                (env.AB_FLAGS, DB_TEST_URL)
                )
            output['db'] += '\n'
            time.sleep(1)
    
        # Disable module
        sudo('a2dismod wsgi')
    
    for k, results in output.items():
        output[k] = results.strip().split('\n')
    
        for line in output[k]:
            if (line.startswith('Failed requests') or \
                line.startswith('Non-2xx responses')) and \
               not line.strip().endswith('0'):
                print '*' * 80
                print '*%s*' % 'INVALID APACHEBENCH RESPONSE'.center(78)
                print '*' * 80
                print line
                
                raise
            elif line.startswith('Requests per second'):
                env.results[k].append(float(re.sub('[^0-9.]', '', line)))
    
    # Get the median of all results
    results = dict(hello=_median(env.results['hello']),
                   tmpl=_median(env.results['tmpl']),
                   db=_median(env.results['db']))
    
    # Update the results file
    env.resultsfp.seek(0)
    results_data = pickle.loads(env.resultsfp.read())
    
    if env.command not in results_data:
        results_data[env.command] = dict()
    if instance.id not in results_data[env.command]:
        results_data[env.command][instance.id] = dict()
    
    results_data[env.command][instance.id]['hello'] = results['hello']
    results_data[env.command][instance.id]['tmpl'] = results['tmpl']
    results_data[env.command][instance.id]['db'] = results['db']
    env.resultsfp.seek(0)
    env.resultsfp.write(pickle.dumps(results_data))
    env.resultsfp.truncate()


@task
@parallel
def uwsgi():
    """Run the Flask uWSGI server test."""
    INSTALL = 'build-essential apache2-utils dtach python-dev python-pip ' \
              'libxml2-dev curl'
    HELLO_TEST_URL = 'http://localhost:9090/'
    TMPL_TEST_URL = 'http://localhost:9090/jinja_hello'
    DB_TEST_URL = 'http://localhost:9090/jinja_sql'
    
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
           exists('/usr/local/lib/python2.6/dist-packages/flask/') and \
           exists('/usr/local/bin/uwsgi') and exists('/usr/bin/dtach'):
            # Kill uWSGI before running it again
            if int(run('ps aux | grep -c uwsgi')) > 2:
                run('killall -9 uwsgi')
        else:
            # Do installs
            sudo('apt-get update')
            sudo('apt-get -y install ' + INSTALL)
            sudo('pip install uwsgi==1.0.4')
            sudo('pip install flask==0.8')
    
        # Setup test environment
        put(here, '/home/ubuntu/', use_sudo=True)
        sudo('rm /home/ubuntu/flask/__init__.*')
        # For good measure
        sudo('chmod -R 777 /home/ubuntu/flask/')
        run('dtach -n /tmp/uwsgi -Ez uwsgi -L --http :9090 --wsgi-file '
            '/home/ubuntu/flask/flask.wsgi')
        time.sleep(1)
        
        # Check the test urls
        if run('curl %s' % HELLO_TEST_URL) != "Hello World!":
            print '*' * 80
            print '*%s*' % 'INVALID WEBSERVER RESPONSE'.center(78)
            print '*' * 80
            
            raise
        elif 'Lorem ipsum' not in run('curl %s' % TMPL_TEST_URL):
            print '*' * 80
            print '*%s*' % 'INVALID WEBSERVER RESPONSE'.center(78)
            print '*' * 80
            
            raise
        elif '1</td><td>Lorem' not in run('curl %s' % DB_TEST_URL):
            print '*' * 80
            print '*%s*' % 'INVALID WEBSERVER RESPONSE'.center(78)
            print '*' * 80
            
            raise
        
        # Run ab
        output = dict(hello='', tmpl='', db='')
        for i in range(env.NUM_AB_TESTS):
            output['hello'] += run(
                'ab %s %s | egrep "(^Failed)|(^Non-2xx)|(^Requests)"' %
                (env.AB_FLAGS, HELLO_TEST_URL)
                )
            output['hello'] += '\n'
            time.sleep(1)
        
        for i in range(env.NUM_AB_TESTS):
            output['tmpl'] += run(
                'ab %s %s | egrep "(^Failed)|(^Non-2xx)|(^Requests)"' %
                (env.AB_FLAGS, TMPL_TEST_URL)
                )
            output['tmpl'] += '\n'
            time.sleep(1)
        
        for i in range(env.NUM_AB_TESTS):
            output['db'] += run(
                'ab %s %s | egrep "(^Failed)|(^Non-2xx)|(^Requests)"' %
                (env.AB_FLAGS, DB_TEST_URL)
                )
            output['db'] += '\n'
            time.sleep(1)
        
        # Terminate instance
        run('killall -9 uwsgi')
    
    for k, results in output.items():
        output[k] = results.strip().split('\n')
    
        for line in output[k]:
            if (line.startswith('Failed requests') or \
                line.startswith('Non-2xx responses')) and \
               not line.strip().endswith('0'):
                print '*' * 80
                print '*%s*' % 'INVALID APACHEBENCH RESPONSE'.center(78)
                print '*' * 80
                print line
                
                raise
            elif line.startswith('Requests per second'):
                env.results[k].append(float(re.sub('[^0-9.]', '', line)))
    
    # Get the median of all results
    results = dict(hello=_median(env.results['hello']),
                   tmpl=_median(env.results['tmpl']),
                   db=_median(env.results['db']))
    
    # Update the results file
    env.resultsfp.seek(0)
    results_data = pickle.loads(env.resultsfp.read())
    
    if env.command not in results_data:
        results_data[env.command] = dict()
    if instance.id not in results_data[env.command]:
        results_data[env.command][instance.id] = dict()
    
    results_data[env.command][instance.id]['hello'] = results['hello']
    results_data[env.command][instance.id]['tmpl'] = results['tmpl']
    results_data[env.command][instance.id]['db'] = results['db']
    env.resultsfp.seek(0)
    env.resultsfp.write(pickle.dumps(results_data))
    env.resultsfp.truncate()


@task
@parallel
def gunicorn():
    """Run the Flask Gunicorn server test."""
    INSTALL = 'build-essential apache2-utils dtach python-dev python-pip curl'
    HELLO_TEST_URL = 'http://localhost:8000/'
    TMPL_TEST_URL = 'http://localhost:8000/jinja_hello'
    DB_TEST_URL = 'http://localhost:8000/jinja_sql'
    
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
           exists('/usr/local/lib/python2.6/dist-packages/flask/') and \
           exists('/usr/local/bin/gunicorn') and exists('/usr/bin/dtach'):
            # Kill gunicorn before running it again
            if int(run('ps aux | grep -c gunicorn')) > 2:
                run('killall -9 gunicorn')
        else:
            # Do installs
            sudo('apt-get update')
            sudo('apt-get -y install ' + INSTALL)
            sudo('pip install gunicorn==0.14.1')
            sudo('pip install flask==0.8')
    
        # Setup test environment
        put(here, '/home/ubuntu/', use_sudo=True)
        sudo('rm /home/ubuntu/flask/__init__.*')
        # For good measure
        sudo('chmod -R 777 /home/ubuntu/flask/')
        with cd('/home/ubuntu/flask/'):
            run('dtach -n /tmp/gunicorn -Ez gunicorn -w 5 flask_app:app')
        time.sleep(1)
        
        # Check the test urls
        if run('curl %s' % HELLO_TEST_URL) != "Hello World!":
            print '*' * 80
            print '*%s*' % 'INVALID WEBSERVER RESPONSE'.center(78)
            print '*' * 80
            
            raise
        elif 'Lorem ipsum' not in run('curl %s' % TMPL_TEST_URL):
            print '*' * 80
            print '*%s*' % 'INVALID WEBSERVER RESPONSE'.center(78)
            print '*' * 80
            
            raise
        elif '1</td><td>Lorem' not in run('curl %s' % DB_TEST_URL):
            print '*' * 80
            print '*%s*' % 'INVALID WEBSERVER RESPONSE'.center(78)
            print '*' * 80
            
            raise
        
        # Run ab
        output = dict(hello='', tmpl='', db='')
        for i in range(env.NUM_AB_TESTS):
            output['hello'] += run(
                'ab %s %s | egrep "(^Failed)|(^Non-2xx)|(^Requests)"' %
                (env.AB_FLAGS, HELLO_TEST_URL)
                )
            output['hello'] += '\n'
            time.sleep(1)
        
        for i in range(env.NUM_AB_TESTS):
            output['tmpl'] += run(
                'ab %s %s | egrep "(^Failed)|(^Non-2xx)|(^Requests)"' %
                (env.AB_FLAGS, TMPL_TEST_URL)
                )
            output['tmpl'] += '\n'
            time.sleep(1)
        
        for i in range(env.NUM_AB_TESTS):
            output['db'] += run(
                'ab %s %s | egrep "(^Failed)|(^Non-2xx)|(^Requests)"' %
                (env.AB_FLAGS, DB_TEST_URL)
                )
            output['db'] += '\n'
            time.sleep(1)
        
        # Terminate instance
        run('killall -9 gunicorn')
    
    for k, results in output.items():
        output[k] = results.strip().split('\n')
    
        for line in output[k]:
            if (line.startswith('Failed requests') or \
                line.startswith('Non-2xx responses')) and \
               not line.strip().endswith('0'):
                print '*' * 80
                print '*%s*' % 'INVALID APACHEBENCH RESPONSE'.center(78)
                print '*' * 80
                print line
                
                raise
            elif line.startswith('Requests per second'):
                env.results[k].append(float(re.sub('[^0-9.]', '', line)))
    
    # Get the median of all results
    results = dict(hello=_median(env.results['hello']),
                   tmpl=_median(env.results['tmpl']),
                   db=_median(env.results['db']))
    
    # Update the results file
    env.resultsfp.seek(0)
    results_data = pickle.loads(env.resultsfp.read())
    
    if env.command not in results_data:
        results_data[env.command] = dict()
    if instance.id not in results_data[env.command]:
        results_data[env.command][instance.id] = dict()
    
    results_data[env.command][instance.id]['hello'] = results['hello']
    results_data[env.command][instance.id]['tmpl'] = results['tmpl']
    results_data[env.command][instance.id]['db'] = results['db']
    env.resultsfp.seek(0)
    env.resultsfp.write(pickle.dumps(results_data))
    env.resultsfp.truncate()


@task
@parallel
def werkzeug():
    """Run the Flask Werkzeug server test."""
    INSTALL = 'build-essential apache2-utils dtach python-dev python-pip curl'
    HELLO_TEST_URL = 'http://localhost:5000/'
    TMPL_TEST_URL = 'http://localhost:5000/jinja_hello'
    DB_TEST_URL = 'http://localhost:5000/jinja_sql'
    
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
           exists('/usr/local/lib/python2.6/dist-packages/flask/') and \
           exists('/usr/local/lib/python2.6/dist-packages/werkzeug/') and \
           exists('/usr/bin/dtach'):
            # Kill werkzeug before running it again
            if int(run('ps aux | grep -c flask')) > 2:
                run('killall -9 python')
        else:
            # Do installs
            sudo('apt-get update')
            sudo('apt-get -y install ' + INSTALL)
            sudo('pip install flask==0.8')
    
        # Setup test environment
        put(here, '/home/ubuntu/', use_sudo=True)
        sudo('rm /home/ubuntu/flask/__init__.*')
        # For good measure
        sudo('chmod -R 777 /home/ubuntu/flask/')
        with cd('/home/ubuntu/flask/'):
            run('dtach -n /tmp/werkzeug -Ez python flask_app.py')
        time.sleep(1)
        
        # Check the test urls
        if run('curl %s' % HELLO_TEST_URL) != "Hello World!":
            print '*' * 80
            print '*%s*' % 'INVALID WEBSERVER RESPONSE'.center(78)
            print '*' * 80
            
            raise
        elif 'Lorem ipsum' not in run('curl %s' % TMPL_TEST_URL):
            print '*' * 80
            print '*%s*' % 'INVALID WEBSERVER RESPONSE'.center(78)
            print '*' * 80
            
            raise
        elif '1</td><td>Lorem' not in run('curl %s' % DB_TEST_URL):
            print '*' * 80
            print '*%s*' % 'INVALID WEBSERVER RESPONSE'.center(78)
            print '*' * 80
            
            raise
        
        # Run ab
        output = dict(hello='', tmpl='', db='')
        for i in range(env.NUM_AB_TESTS):
            output['hello'] += run(
                'ab %s %s | egrep "(^Failed)|(^Non-2xx)|(^Requests)"' %
                (env.AB_FLAGS, HELLO_TEST_URL)
                )
            output['hello'] += '\n'
            time.sleep(1)
        
        for i in range(env.NUM_AB_TESTS):
            output['tmpl'] += run(
                'ab %s %s | egrep "(^Failed)|(^Non-2xx)|(^Requests)"' %
                (env.AB_FLAGS, TMPL_TEST_URL)
                )
            output['tmpl'] += '\n'
            time.sleep(1)
        
        for i in range(env.NUM_AB_TESTS):
            output['db'] += run(
                'ab %s %s | egrep "(^Failed)|(^Non-2xx)|(^Requests)"' %
                (env.AB_FLAGS, DB_TEST_URL)
                )
            output['db'] += '\n'
            time.sleep(1)
        
        # Terminate instance
        run('killall -9 python')
    
    for k, results in output.items():
        output[k] = results.strip().split('\n')
    
        for line in output[k]:
            if (line.startswith('Failed requests') or \
                line.startswith('Non-2xx responses')) and \
               not line.strip().endswith('0'):
                print '*' * 80
                print '*%s*' % 'INVALID APACHEBENCH RESPONSE'.center(78)
                print '*' * 80
                print line
                
                raise
            elif line.startswith('Requests per second'):
                env.results[k].append(float(re.sub('[^0-9.]', '', line)))
    
    # Get the median of all results
    results = dict(hello=_median(env.results['hello']),
                   tmpl=_median(env.results['tmpl']),
                   db=_median(env.results['db']))
    
    # Update the results file
    env.resultsfp.seek(0)
    results_data = pickle.loads(env.resultsfp.read())
    
    if env.command not in results_data:
        results_data[env.command] = dict()
    if instance.id not in results_data[env.command]:
        results_data[env.command][instance.id] = dict()
    
    results_data[env.command][instance.id]['hello'] = results['hello']
    results_data[env.command][instance.id]['tmpl'] = results['tmpl']
    results_data[env.command][instance.id]['db'] = results['db']
    env.resultsfp.seek(0)
    env.resultsfp.write(pickle.dumps(results_data))
    env.resultsfp.truncate()
