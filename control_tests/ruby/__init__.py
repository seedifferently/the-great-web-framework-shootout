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
def passenger(run_tests=True):
    """Run the Ruby mod_passenger control test."""
    INSTALL = 'build-essential apache2-mpm-worker apache2-dev apache2-utils ' \
              'libcurl4-openssl-dev libsqlite3-dev libyaml-dev curl'
    RUBY_URL = 'http://ftp.ruby-lang.org/pub/ruby/1.9/ruby-1.9.3-p125.tar.gz'
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
        if exists('/usr/sbin/ab') and exists('/usr/local/bin/gem') and \
           exists('/etc/apache2/mods-available/passenger.load') and \
           exists('/usr/sbin/apache2ctl') and \
           sudo('apache2ctl -V | '
                'grep -m 1 "Server MPM"').strip().endswith('Worker'):
            sudo('a2enmod passenger')
        else:
            # Check requirements
            if not exists('/usr/local/bin/ruby') or \
               not exists('/usr/local/bin/gem'):
                sudo('apt-get update')
                sudo('apt-get -y install ' + INSTALL)
                if exists('/home/ubuntu/ruby-1.9.3-p125.tar.gz'):
                    run('rm -rf /home/ubuntu/ruby-1.9.3-p125*')
                run('wget %s' % RUBY_URL)
                run('tar -zxvf ruby-1.9.3-p125.tar.gz')
                print '[%s] Building Ruby...' % env.host
                with cd('ruby-1.9.3-p125'):
                    run('./configure')
                    run('make')
                    sudo('make install')
            
            # Do installs
            sudo('apt-get update')
            sudo('apt-get -y install ' + INSTALL)
            sudo('gem install passenger -v 3.0.11 --no-rdoc --no-ri')
            sudo('passenger-install-apache2-module --auto')
            put(os.path.join(here, 'passenger.load'),
                '/etc/apache2/mods-available/', use_sudo=True)
            sudo('a2enmod passenger')
        
        if run_tests is False or run_tests == 'False':
            return
        
        # Setup test environment
        sudo('a2dissite 000-default')
        put(os.path.join(here, 'vhost.conf'),
            '/etc/apache2/sites-enabled/', use_sudo=True)
        put(here, '/var/www/', use_sudo=True)
        # For good measure
        sudo('chmod -R 777 /var/www/ruby/')
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
        sudo('a2dismod passenger')
    
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
def thin(run_tests=True):
    """Run the Ruby Thin server control test."""
    INSTALL = 'build-essential apache2-utils dtach libcurl4-openssl-dev ' \
              'libsqlite3-dev libyaml-dev curl'
    RUBY_URL = 'http://ftp.ruby-lang.org/pub/ruby/1.9/ruby-1.9.3-p125.tar.gz'
    TEST_URL = 'http://localhost:3000/'
    
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
        if exists('/usr/sbin/ab') and exists('/usr/local/bin/gem') and \
           exists('/usr/local/bin/thin') and exists('/usr/bin/dtach'):
            # Kill thin before running it again
            if int(run('ps aux | grep -c thin')) > 2:
                sudo('killall -9 thin')
        else:
            # Check requirements
            if not exists('/usr/local/bin/ruby') or \
               not exists('/usr/local/bin/gem'):
                sudo('apt-get update')
                sudo('apt-get -y install ' + INSTALL)
                if exists('/home/ubuntu/ruby-1.9.3-p125.tar.gz'):
                    run('rm -rf /home/ubuntu/ruby-1.9.3-p125*')
                run('wget %s' % RUBY_URL)
                run('tar -zxvf ruby-1.9.3-p125.tar.gz')
                print '[%s] Building Ruby...' % env.host
                with cd('ruby-1.9.3-p125'):
                    run('./configure')
                    run('make')
                    sudo('make install')
            
            # Do installs
            sudo('apt-get update')
            sudo('apt-get -y install ' + INSTALL)
            sudo('gem install thin -v 1.3.1 --no-rdoc --no-ri')
    
        # Setup test environment
        put(here, '/home/ubuntu/', use_sudo=True)
        # For good measure
        sudo('chmod -R 777 /home/ubuntu/ruby/')
        run('dtach -n /tmp/thin -Ez thin -c /home/ubuntu/ruby/ start')
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
        sudo('killall -9 thin')
    
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
def unicorn(run_tests=True):
    """Run the Ruby Unicorn server control test."""
    INSTALL = 'build-essential apache2-utils dtach libcurl4-openssl-dev ' \
              'libsqlite3-dev libyaml-dev curl'
    RUBY_URL = 'http://ftp.ruby-lang.org/pub/ruby/1.9/ruby-1.9.3-p125.tar.gz'
    TEST_URL = 'http://localhost:8080/'
    
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
        if exists('/usr/sbin/ab') and exists('/usr/local/bin/gem') and \
           exists('/usr/local/bin/unicorn') and exists('/usr/bin/dtach'):
            # Kill unicorn before running it again
            if int(run('ps aux | grep -c unicorn')) > 2:
                sudo('killall -9 unicorn')
        else:
            # Check requirements
            if not exists('/usr/local/bin/ruby') or \
               not exists('/usr/local/bin/gem'):
                sudo('apt-get update')
                sudo('apt-get -y install ' + INSTALL)
                if exists('/home/ubuntu/ruby-1.9.3-p125.tar.gz'):
                    run('rm -rf /home/ubuntu/ruby-1.9.3-p125*')
                run('wget %s' % RUBY_URL)
                run('tar -zxvf ruby-1.9.3-p125.tar.gz')
                print '[%s] Building Ruby...' % env.host
                with cd('ruby-1.9.3-p125'):
                    run('./configure')
                    run('make')
                    sudo('make install')
            
            # Do installs
            sudo('apt-get update')
            sudo('apt-get -y install ' + INSTALL)
            sudo('gem install unicorn -v 4.2.0 --no-rdoc --no-ri')
    
        # Setup test environment
        put(here, '/home/ubuntu/', use_sudo=True)
        # For good measure
        sudo('chmod -R 777 /home/ubuntu/ruby/')
        with cd('/home/ubuntu/ruby/'):
            run('dtach -n /tmp/unicorn -Ez unicorn -E production')
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
        sudo('killall -9 unicorn')
    
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
