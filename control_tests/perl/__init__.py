import sys, os, time, re, pickle
from fabric.state import env
from fabric.decorators import task, parallel
from fabric.operations import put, run, sudo
from fabric.context_managers import hide, settings
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
def plack(run_tests=True):
    """Run the Perl Plack control test."""
    INSTALL = 'build-essential dtach apache2-utils libdigest-sha1-perl curl'
    TEST_URL = 'http://localhost:5000/'
    
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
        if exists('/usr/local/bin/plackup') and exists('/usr/bin/dtach'):
            # Kill plackup before running it again
            if int(run('ps aux | grep -c plackup')) > 2:
                sudo('killall -9 plackup')
        else:
            # Do installs
            sudo('apt-get update')
            sudo('apt-get -y install ' + INSTALL)
            print '[%s] Building Plack from CPAN...' % env.host
#            sudo('PERL_MM_USE_DEFAULT=1 cpan -fi Task::Plack')
            sudo('curl -L http://cpanmin.us | perl - --sudo App::cpanminus')
            sudo('cpanm -n Task::Plack --force')
        
        if run_tests is False or run_tests == 'False':
            return
        
        # Setup test environment
        put(here, '/home/ubuntu/')
        # For good measure
        sudo('chmod -R 777 /home/ubuntu/perl/')
        run('dtach -n /tmp/plackup -Ez plackup -E deployment '
            '/home/ubuntu/perl/perl.psgi')
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
    
        # Terminate instance
        sudo('killall -9 plackup')
    
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
def mod_perl(run_tests=True):
    """Run the Perl mod_perl 2 control test."""
    INSTALL = 'libapache2-mod-perl2 curl'
    TEST_URL = 'http://localhost/perl.pl'
    
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
        if exists('/etc/apache2/mods-available/perl.load') and \
           exists('/usr/sbin/apache2ctl') and \
           sudo('apache2ctl -V | '
                'grep -m 1 "Server MPM"').strip().endswith('Worker'):
            sudo('a2enmod perl')
        else:
            # Do installs
            sudo('apt-get update')
            sudo('apt-get -y install ' + INSTALL)
            sudo('a2enmod perl')
        
        if run_tests is False or run_tests == 'False':
            return
        
        # Setup test environment
        sudo('a2dissite 000-default')
        put(os.path.join(here, 'vhost.conf'),
            '/etc/apache2/sites-enabled/', use_sudo=True)
        put(here, '/var/www/', use_sudo=True)
        # For good measure
        sudo('chmod -R 777 /var/www/perl')
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
        sudo('a2dismod perl')
    
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
