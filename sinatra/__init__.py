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
def passenger():
    """Run the Sinatra mod_passenger test."""
    HELLO_TEST_URL = 'http://localhost/'
    TMPL_TEST_URL = 'http://localhost/erb_hello'
    DB_TEST_URL = 'http://localhost/erb_sql'
    
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
        if exists('/usr/local/lib/ruby/gems/1.9.1/gems/sinatra-1.3.2/') and \
           exists('/usr/local/lib/ruby/gems/1.9.1/gems/sqlite3-1.3.5/') and \
           exists('/etc/apache2/mods-available/passenger.load') and \
           exists('/usr/sbin/apache2ctl') and \
           sudo('apache2ctl -V | '
                'grep -m 1 "Server MPM"').strip().endswith('Worker'):
            sudo('a2enmod passenger')
        else:
            # Check requirements
            if not exists('/usr/local/bin/gem') or \
               not exists('/etc/apache2/mods-available/passenger.load') or \
               not sudo('apache2ctl -V | grep '
                        '-m 1 "Server MPM"').strip().endswith('Worker'):
                print '\nERROR: Required dependencies have not yet been ' \
                      'installed. Please run the "ruby.mod_passenger" task ' \
                      'at least once before running this task.\n'
                sys.exit(1)
            
            # Do installs
            sudo('gem install sinatra -v 1.3.2 --no-rdoc --no-ri')
            sudo('gem install sqlite3 -v 1.3.5 --no-rdoc --no-ri')
            sudo('a2enmod passenger')
    
        # Setup test environment
        sudo('a2dissite 000-default')
        put(os.path.join(here, 'vhost.conf'),
            '/etc/apache2/sites-enabled/', use_sudo=True)
        put(here, '/var/www/', use_sudo=True)
        # For good measure
        sudo('chmod -R 777 /var/www/sinatra/')
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
        sudo('a2dismod passenger')
    
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
def thin():
    """Run the Sinatra thin server test."""
    HELLO_TEST_URL = 'http://localhost:3000/'
    TMPL_TEST_URL = 'http://localhost:3000/erb_hello'
    DB_TEST_URL = 'http://localhost:3000/erb_sql'
    
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
        if exists('/usr/local/lib/ruby/gems/1.9.1/gems/sinatra-1.3.2/') and \
           exists('/usr/local/lib/ruby/gems/1.9.1/gems/sqlite3-1.3.5/') and \
           exists('/usr/sbin/ab') and exists('/usr/local/bin/gem') and \
           exists('/usr/local/bin/thin') and exists('/usr/bin/dtach'):
            # Kill thin before running it again
            if int(run('ps aux | grep -c thin')) > 2:
                sudo('killall -9 thin')
        else:
            # Check requirements
            if not exists('/usr/local/bin/gem'):
                print '\nERROR: Required dependencies have not yet been ' \
                      'installed. Please run the "ruby.thin" task at least ' \
                      'once before running this task.\n'
                sys.exit(1)
            
            # Do installs
            sudo('gem install thin -v 1.3.1 --no-rdoc --no-ri')
            sudo('gem install sinatra -v 1.3.2 --no-rdoc --no-ri')
            sudo('gem install sqlite3 -v 1.3.5 --no-rdoc --no-ri')
    
        # Setup test environment
        put(here, '/var/www/', use_sudo=True)
        # For good measure
        sudo('chmod -R 777 /var/www/sinatra/')
        run('dtach -n /tmp/sinatra -Ez thin -c /var/www/sinatra/ start')
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
        sudo('killall -9 thin')
    
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
def unicorn():
    """Run the Sinatra unicorn server test."""
    HELLO_TEST_URL = 'http://localhost:8080/'
    TMPL_TEST_URL = 'http://localhost:8080/erb_hello'
    DB_TEST_URL = 'http://localhost:8080/erb_sql'
    
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
        if exists('/usr/local/lib/ruby/gems/1.9.1/gems/sinatra-1.3.2/') and \
           exists('/usr/local/lib/ruby/gems/1.9.1/gems/sqlite3-1.3.5/') and \
           exists('/usr/sbin/ab') and exists('/usr/local/bin/gem') and \
           exists('/usr/local/bin/unicorn') and exists('/usr/bin/dtach'):
            # Kill unicorn before running it again
            if int(run('ps aux | grep -c unicorn')) > 2:
                sudo('killall -9 unicorn')
        else:
            # Check requirements
            if not exists('/usr/local/bin/gem'):
                print '\nERROR: Required dependencies have not yet been ' \
                      'installed. Please run the "ruby.unicorn" task at ' \
                      'least once before running this task.\n'
                sys.exit(1)
            
            # Do installs
            sudo('gem install unicorn -v 4.2.0 --no-rdoc --no-ri')
            sudo('gem install sinatra -v 1.3.2 --no-rdoc --no-ri')
            sudo('gem install sqlite3 -v 1.3.5 --no-rdoc --no-ri')
    
        # Setup test environment
        put(here, '/var/www/', use_sudo=True)
        # For good measure
        sudo('chmod -R 777 /var/www/sinatra/')
        with cd('/var/www/sinatra/'):
            run('dtach -n /tmp/unicorn -Ez unicorn -E production')
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
        sudo('killall -9 unicorn')
    
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
