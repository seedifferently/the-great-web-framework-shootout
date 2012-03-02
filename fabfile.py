"""
Benchmark test runner for The Great Web Framework Shootout.

Usage: fab test <test task(s)> cleanup

Type "fab -l" for a full list of tasks.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHOR BE
LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import sys, os, time, inspect, re, tempfile, pickle
from fabric.decorators import task, parallel, serial
from fabric.api import run, sudo, put, env, settings, hide
from fabric.context_managers import cd
from fabric.contrib.files import exists
from fabric.tasks import execute
from boto import ec2


################################################################################
#                                                                              #
#                       DEFINE YOUR AWS AND EC2 SETTINGS                       #
#                                                                              #
################################################################################
AWS_ACCESS_KEY = None # specify, or get from .boto config
AWS_SECRET_KEY = None # specify, or get from .boto config
EC2_AMI_ID = 'ami-5c9b4935'
EC2_INSTANCE_TYPE = 'm1.large'
EC2_REGION = 'us-east-1'
EC2_SSH_KEY_NAME = 'id_rsa'
# EC2_SSH_KEY_PATH = '~/.ssh/id_rsa.pub'
EC2_SECURITY_GROUPS = ['default']


################################################################################
#                                                                              #
#                           DEFINE THE TEST SETTINGS                           #
#                                                                              #
################################################################################
# Use START_EC2_INSTANCES to run tests on new instances, or USE_EC2_INSTANCES to
# run tests on existing instances, or USE_OTHER_INSTANCES to run tests on other
# hosts as mock instances.
START_EC2_INSTANCES = 5 # number of instances to run tests on
# -OR-
#USE_EC2_INSTANCES = ['i-d9738bbd'] # Or set to None for all running instances
# -OR-
#class mock_instance(object):
#    """Simulates an EC2 instance object so that you can specify your own hosts
#    to run the tests on."""
#    def __init__(self, id, host):
#        self.id = id
#        self.public_dns_name = host
#instance1 = mock_instance('Host 1', '192.168.56.101')
#instance2 = mock_instance('Host 2', '192.168.56.102')
#USE_OTHER_INSTANCES = [instance1, instance2]

TERMINATE_INSTANCES = True # terminate instances after completion of tests?
NUM_AB_TESTS = 10 # number of times to run apachebench
AB_FLAGS = '-q -c 10 -n 25000' # apachebench flags to use



HEADER = """
================================================================================
The Great Web Framework Shootout
================================================================================

Below are the results of your tests across %s instance(s):
"""

TEMPLATE = """
%s test
--------------------------------------------------------------------------------

=============        =====  =====  =====
Instance                 Median reqs/sec
-------------        -------------------
ID                   hello   tmpl     db
=============        =====  =====  =====
%s
-------------        -----  -----  -----
AVERAGE TOTAL        %5s  %5s  %5s
=============        =====  =====  =====
"""

here = os.path.abspath(os.path.dirname(__file__))

conn = ec2.connect_to_region(EC2_REGION,
                             aws_access_key_id=AWS_ACCESS_KEY,
                             aws_secret_access_key=AWS_SECRET_KEY)

def _ec2_instance(quantity):
    return conn.run_instances(
        EC2_AMI_ID, min_count=quantity, max_count=quantity,
        key_name=EC2_SSH_KEY_NAME, instance_type=EC2_INSTANCE_TYPE,
        security_groups=EC2_SECURITY_GROUPS
        )

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
def test():
    """
    Test preloader. Run this before any other tasks.
    """
    if sys.argv[-1] != 'cleanup':
        print '\nERROR: You must run "cleanup" as the final task. Run "fab ' \
              '-l" for more information and a complete list of tasks.\n'
        sys.exit(1)
    
    env.connection_attempts = 10
    env.timeout = 30
    env.disable_known_hosts = True
    env.reject_unknown_hosts = False
#    env.key_filename = EC2_SSH_KEY_PATH
    env.user = 'ubuntu'
    env.hosts = []
    env.results = []
    env.resultsfp = tempfile.TemporaryFile()
    env.resultsfp.write(pickle.dumps(dict()))
    
    # Prepare EC2 Instances
    try:
        if START_EC2_INSTANCES:
            env.instances = _ec2_instance(START_EC2_INSTANCES).instances
            
            print "Please wait while Fabric boots up %s instances of %s..." % (
                START_EC2_INSTANCES, EC2_AMI_ID
                )
            
            time.sleep(20)
            
            for instance in env.instances:
                instance.update()
                
                while instance.state != 'running':
                    if instance.state != 'pending':
                        print 'ERROR: Unsupported instance state for %s: %s' % (
                            instance.id, instance.state
                            )
                        
                        # Shut down everything if specified
                        if TERMINATE_INSTANCES and \
                           hasattr(env.instances[0], 'state'):
                            instances = [instance.id for instance in
                                         env.instances]
                        else:
                            instances = None
                        
                        if instances:
                            conn.terminate_instances(instances)
                        
                        sys.exit(1)
                    
                    instance.update()
                    time.sleep(5)
    except NameError:
        try:
            reservations = conn.get_all_instances(
                USE_EC2_INSTANCES,
                filters={'instance-state-name': 'running'}
                )
            env.instances = []
            
            for reservation in reservations:
                env.instances.extend(reservation.instances)
            
            if not env.instances:
                print '\nERROR: None of the instances you specified seem to ' \
                      'running. Please check your USE_EC2_INSTANCES settings.\n'
                sys.exit(1)
        except NameError:
            try:
                env.instances = USE_OTHER_INSTANCES
            except NameError:
                print '\nERROR: You must specify either START_EC2_INSTANCES, ' \
                      'USE_EC2_INSTANCES, or USE_OTHER_INSTANCES in the TEST ' \
                      'SETTINGS section.\n'
                sys.exit(1)
    
    env.hosts = [instance.public_dns_name for instance in env.instances]
    
    print "\nYour instances are ready! Please wait while Fabric sets up the " \
          "test environment and runs the tests (which may take a very long " \
          "time)...\n"


@task
@serial
def cleanup():
    """
    Test cleanup. Run this after any other tasks.
    """
    if env.host == env.hosts[0]:
        if TERMINATE_INSTANCES and hasattr(env.instances[0], 'state'):
            instances = [instance.id for instance in env.instances]
        else:
            instances = None
        
        if instances:
            conn.terminate_instances(instances)
    
    if env.host == env.hosts[-1]:
        env.resultsfp.seek(0)
        results_data = pickle.loads(env.resultsfp.read())
        
        print HEADER % len(env.instances)
        
        for test_name, tests in results_data.items():
            # Prepare printout
            results_printout = ''
            average = dict(hello = [], tmpl=[], db=[])
            
            for instance_name, results in tests.items():
                if isinstance(results['hello'], int) and \
                   average['hello'] != 'n/a':
                    average['hello'].append(results['hello'])
                else:
                    average['hello'] = 'n/a'
                if isinstance(results['tmpl'], int) and \
                   average['tmpl'] != 'n/a':
                    average['tmpl'].append(results['tmpl'])
                else:
                    average['tmpl'] = 'n/a'
                if isinstance(results['db'], int) and \
                   average['db'] != 'n/a':
                    average['db'].append(results['db'])
                else:
                    average['db'] = 'n/a'
                
                results_printout += '%-13s        %5s  %5s  %5s\n' % \
                                    (instance_name[:13], results['hello'],
                                    results['tmpl'], results['db'])
            
            if average['hello'] != 'n/a':
                average['hello'] = '%s' % _average(average['hello'])
            if average['tmpl'] != 'n/a':
                average['tmpl'] = '%s' % _average(average['tmpl'])
            if average['db'] != 'n/a':
                average['db'] = '%s' % _average(average['db'])
            
            print TEMPLATE % (test_name, results_printout.strip(),
                              average['hello'], average['tmpl'], average['db'])


@task
@parallel
def apache(run_tests=True):
    """
    Run the Apache 2 control test.
    """
    INSTALL = 'apache2'
    TEST_URL = 'http://localhost/apache.html'
    
    # Check the correct usage
    if sys.argv[1] != 'test':
        print '\nERROR: You must run "test" as the first task. Run "fab -l" ' \
              'for more information and a complete list of tasks.\n'
        sys.exit(1)
    
    # Get current instance info
    for instance in env.instances:
        if instance.public_dns_name == env.host:
            current_instance = instance
    
    try:
        if exists('/usr/sbin/apache2'):
            pass
        else:
            # Do installs
            with settings(hide('running', 'stdout')):
                sudo('apt-get -y install ' + INSTALL)
        
        if run_tests is False:
            return
        
        # Setup test environment
        with settings(hide('running', 'stdout')):
            sudo('a2dissite 000-default')
            put(os.path.join(here, 'control_tests', 'apache', 'vhost.conf'),
                '/etc/apache2/sites-enabled/', use_sudo=True)
            put(os.path.join(here, 'control_tests', 'apache', 'apache.html'),
                '/var/www/', use_sudo=True)
            # For good measure
            sudo('chmod -R 777 /var/www')
            sudo('apache2ctl restart')
        
        with settings(hide('running', 'stdout')):
            if run('curl %s' % TEST_URL) != "Hello World!":
                print '*' * 80
                print '*%s*' % 'INVALID WEBSERVER RESPONSE'.center(78)
                print '*' * 80
                
                raise
        
        output = ''
        for i in range(NUM_AB_TESTS):
            with settings(hide('running', 'stdout')):
                output += run(
                    'ab %s %s | egrep "(^Failed)|(^Non-2xx)|(^Requests)"' %
                    (AB_FLAGS, TEST_URL)
                    )
                output += '\n'
                time.sleep(1)
        
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
                env.results.append(float(re.sub('[^0-9.]', '', line)))
        
        # Get the median of all results
        result = _median(env.results)
        
        # Update the results file
        env.resultsfp.seek(0)
        results_data = pickle.loads(env.resultsfp.read())
        
        if env.command not in results_data:
            results_data[env.command] = dict()
        if current_instance.id not in results_data[env.command]:
            results_data[env.command][current_instance.id] = dict()
        
        results_data[env.command][current_instance.id]['hello'] = result
        results_data[env.command][current_instance.id]['tmpl'] = 'n/a'
        results_data[env.command][current_instance.id]['db'] = 'n/a'
        env.resultsfp.seek(0)
        env.resultsfp.write(pickle.dumps(results_data))
        env.resultsfp.truncate()
    
    except Exception, e:
        print '*' * 80
        print '*%s*' % 'ABORTING DUE TO RUNTIME ERROR'.center(78)
        print '*' * 80
        
        raise e


@task
@parallel
def mod_php(run_tests=True):
    """Run the PHP mod_php control test."""
    INSTALL = 'libapache2-mod-php5 php-apc'
    TEST_URL = 'http://localhost/php.php'
    
    apache(run_tests=False)
    
    # Check the correct usage
    if sys.argv[1] != 'test':
        print '\nERROR: You must run "test" as the first task. Run "fab -l" ' \
              'for more information and a complete list of tasks.\n'
        sys.exit(1)
    
    # Get current instance info
    for instance in env.instances:
        if instance.public_dns_name == env.host:
            current_instance = instance
    
    try:
        if exists('/etc/apache2/mods-available/php5.load'):
            with settings(hide('running', 'stdout')):
                sudo('a2enmod php5')
        else:
            # Do installs
            with settings(hide('running', 'stdout')):
                sudo('apt-get -y install ' + INSTALL)
                sudo('a2enmod php5')
        
        if run_tests is False:
            return
        
        # Setup test environment
        with settings(hide('running', 'stdout')):
            sudo('a2dissite 000-default')
            put(os.path.join(here, 'control_tests', 'mod_php', 'vhost.conf'),
                '/etc/apache2/sites-enabled/', use_sudo=True)
            put(os.path.join(here, 'control_tests', 'mod_php'), '/var/www/',
                use_sudo=True)
            # For good measure
            sudo('chmod -R 777 /var/www')
            sudo('apache2ctl restart')
        
        with settings(hide('running', 'stdout')):
            if run('curl %s' % TEST_URL) != "Hello World!":
                print '*' * 80
                print '*%s*' % 'INVALID WEBSERVER RESPONSE'.center(78)
                print '*' * 80
                
                raise
        
        output = ''
        for i in range(NUM_AB_TESTS):
            with settings(hide('running', 'stdout')):
                output += run(
                    'ab %s %s | egrep "(^Failed)|(^Non-2xx)|(^Requests)"' %
                    (AB_FLAGS, TEST_URL)
                    )
                output += '\n'
                time.sleep(1)
        
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
                env.results.append(float(re.sub('[^0-9.]', '', line)))
        
        # Get the median of all results
        result = _median(env.results)
        
        # Update the results file
        env.resultsfp.seek(0)
        results_data = pickle.loads(env.resultsfp.read())
        
        if env.command not in results_data:
            results_data[env.command] = dict()
        if current_instance.id not in results_data[env.command]:
            results_data[env.command][current_instance.id] = dict()
        
        results_data[env.command][current_instance.id]['hello'] = result
        results_data[env.command][current_instance.id]['tmpl'] = 'n/a'
        results_data[env.command][current_instance.id]['db'] = 'n/a'
        env.resultsfp.seek(0)
        env.resultsfp.write(pickle.dumps(results_data))
        env.resultsfp.truncate()
    
    except Exception, e:
        print '*' * 80
        print '*%s*' % 'ABORTING DUE TO RUNTIME ERROR'.center(78)
        print '*' * 80
        
        raise e


@task
@parallel
def mod_wsgi(run_tests=True):
    """Run the Python mod_wsgi control test."""
    INSTALL = 'libapache2-mod-wsgi'
    TEST_URL = 'http://localhost/'
    
    # Check the correct usage
    if sys.argv[1] != 'test':
        print '\nERROR: You must run "test" as the first task. Run "fab -l" ' \
              'for more information and a complete list of tasks.\n'
        sys.exit(1)
    
    # Get current instance info
    for instance in env.instances:
        if instance.public_dns_name == env.host:
            current_instance = instance
    
    try:
        if exists('/etc/apache2/mods-available/wsgi.load'):
            with settings(hide('running', 'stdout')):
                sudo('a2enmod wsgi')
        else:
            # Do installs
            with settings(hide('running', 'stdout')):
                sudo('apt-get -y install ' + INSTALL)
                sudo('a2enmod wsgi')
        
        if run_tests is False:
            return
        
        # Setup test environment
        with settings(hide('running', 'stdout')):
            sudo('a2dissite 000-default')
            put(os.path.join(here, 'control_tests', 'mod_wsgi', 'vhost.conf'),
                '/etc/apache2/sites-enabled/', use_sudo=True)
            put(os.path.join(here, 'control_tests', 'mod_wsgi'), '/var/www/',
                             use_sudo=True)
            # For good measure
            sudo('chmod -R 777 /var/www')
            sudo('apache2ctl restart')
        
        with settings(hide('running', 'stdout')):
            if run('curl %s' % TEST_URL) != "Hello World!":
                print '*' * 80
                print '*%s*' % 'INVALID WEBSERVER RESPONSE'.center(78)
                print '*' * 80
                
                raise
        
        output = ''
        for i in range(NUM_AB_TESTS):
            with settings(hide('running', 'stdout')):
                output += run(
                    'ab %s %s | egrep "(^Failed)|(^Non-2xx)|(^Requests)"' %
                    (AB_FLAGS, TEST_URL)
                    )
                output += '\n'
                time.sleep(1)
        
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
                env.results.append(float(re.sub('[^0-9.]', '', line)))
        
        # Get the median of all results
        result = _median(env.results)
        
        # Update the results file
        env.resultsfp.seek(0)
        results_data = pickle.loads(env.resultsfp.read())
        
        if env.command not in results_data:
            results_data[env.command] = dict()
        if current_instance.id not in results_data[env.command]:
            results_data[env.command][current_instance.id] = dict()
        
        results_data[env.command][current_instance.id]['hello'] = result
        results_data[env.command][current_instance.id]['tmpl'] = 'n/a'
        results_data[env.command][current_instance.id]['db'] = 'n/a'
        env.resultsfp.seek(0)
        env.resultsfp.write(pickle.dumps(results_data))
        env.resultsfp.truncate()
    
    except Exception, e:
        print '*' * 80
        print '*%s*' % 'ABORTING DUE TO RUNTIME ERROR'.center(78)
        print '*' * 80
        
        raise e


@task
@parallel
def mod_passenger(run_tests=True):
    """Run the Ruby mod_passenger control test."""
    INSTALL = 'build-essential apache2 apache2-dev apache2-utils ' \
              'libcurl4-openssl-dev'
    RUBY_URL = 'http://ftp.ruby-lang.org/pub/ruby/1.9/ruby-1.9.3-p125.tar.gz'
    TEST_URL = 'http://localhost/'
    
    # Check the correct usage
    if sys.argv[1] != 'test':
        print '\nERROR: You must run "test" as the first task. Run "fab -l" ' \
              'for more information and a complete list of tasks.\n'
        sys.exit(1)
    
    # Get current instance info
    for instance in env.instances:
        if instance.public_dns_name == env.host:
            current_instance = instance
    
    try:
        if exists('/etc/apache2/mods-available/passenger.load'):
            with settings(hide('running', 'stdout')):
                sudo('a2enmod passenger')
        else:
            # Do installs
            with settings(hide('running', 'stdout')):
                sudo('apt-get -y install ' + INSTALL)
                run('wget %s' % RUBY_URL)
                run('tar -zxvf ruby-1.9.3-p125.tar.gz')
                with cd('ruby-1.9.3-p125'):
                    run('./configure')
                    run('make')
                    sudo('make install')
                
                sudo('gem install passenger -v 3.0.11 --no-rdoc --no-ri')
                sudo('passenger-install-apache2-module --auto')
                put(os.path.join(here, 'control_tests', 'mod_passenger',
                                 'passenger.load'),
                    '/etc/apache2/mods-available/', use_sudo=True)
                sudo('a2enmod passenger')
        
        if run_tests is False:
            return
        
        # Setup test environment
        with settings(hide('running', 'stdout')):
            sudo('a2dissite 000-default')
            put(os.path.join(here, 'control_tests', 'mod_passenger',
                             'vhost.conf'),
                '/etc/apache2/sites-enabled/', use_sudo=True)
            put(os.path.join(here, 'control_tests', 'mod_passenger'),
                '/var/www/', use_sudo=True)
            # For good measure
            sudo('chmod -R 777 /var/www')
            sudo('apache2ctl restart')
        
        with settings(hide('running', 'stdout')):
            if run('curl %s' % TEST_URL) != "Hello World!":
                print '*' * 80
                print '*%s*' % 'INVALID WEBSERVER RESPONSE'.center(78)
                print '*' * 80
                
                raise
        
        output = ''
        for i in range(NUM_AB_TESTS):
            with settings(hide('running', 'stdout')):
                output += run(
                    'ab %s %s | egrep "(^Failed)|(^Non-2xx)|(^Requests)"' %
                    (AB_FLAGS, TEST_URL)
                    )
                output += '\n'
                time.sleep(1)
        
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
                env.results.append(float(re.sub('[^0-9.]', '', line)))
        
        # Get the median of all results
        result = _median(env.results)
        
        # Update the results file
        env.resultsfp.seek(0)
        results_data = pickle.loads(env.resultsfp.read())
        
        if env.command not in results_data:
            results_data[env.command] = dict()
        if current_instance.id not in results_data[env.command]:
            results_data[env.command][current_instance.id] = dict()
        
        results_data[env.command][current_instance.id]['hello'] = result
        results_data[env.command][current_instance.id]['tmpl'] = 'n/a'
        results_data[env.command][current_instance.id]['db'] = 'n/a'
        env.resultsfp.seek(0)
        env.resultsfp.write(pickle.dumps(results_data))
        env.resultsfp.truncate()
    
    except Exception, e:
        print '*' * 80
        print '*%s*' % 'ABORTING DUE TO RUNTIME ERROR'.center(78)
        print '*' * 80
        
        raise e


@task
@parallel
def plack(run_tests=True):
    """Run the Perl Plack control test."""
    INSTALL = 'build-essential dtach apache2-utils libdigest-sha1-perl'
    TEST_URL = 'http://localhost:5000/'
    
    # Check the correct usage
    if sys.argv[1] != 'test':
        print '\nERROR: You must run "test" as the first task. Run "fab -l" ' \
              'for more information and a complete list of tasks.\n'
        sys.exit(1)
    
    # Get current instance info
    for instance in env.instances:
        if instance.public_dns_name == env.host:
            current_instance = instance
    try:
        if exists('/usr/local/bin/plackup') and exists('/usr/bin/dtach'):
            pass
        else:
            # Do installs
            with settings(hide('running', 'stdout')):
                sudo('apt-get -y install ' + INSTALL)
#                sudo('PERL_MM_USE_DEFAULT=1 cpan -fi Task::Plack')
                sudo('curl -L http://cpanmin.us | perl - --sudo App::cpanminus')
                sudo('cpanm -n Task::Plack --force')
        
        if run_tests is False:
            return
        
        # Setup test environment
        with settings(hide('running', 'stdout')):
            put(os.path.join(here, 'control_tests', 'plack'), '/home/ubuntu/')
            # For good measure
            sudo('chmod -R 777 /home/ubuntu/plack/')
            # Kill the last instance of plackup before running it again
            run('pid=$(ps aux | sort -r | grep -v grep | grep -m 1 plackup | ' \
                'awk \'{print $2}\'); if [ $pid ]; then kill -9 $pid; fi')
            run('dtach -n /tmp/plackup -Ez plackup -E deployment '
                '/home/ubuntu/plack/perl.psgi')
            time.sleep(1)
        
        with settings(hide('running', 'stdout')):
            if run('curl %s' % TEST_URL) != "Hello World!":
                print '*' * 80
                print '*%s*' % 'INVALID WEBSERVER RESPONSE'.center(78)
                print '*' * 80
                
                raise
        
        output = ''
        for i in range(NUM_AB_TESTS):
            with settings(hide('running', 'stdout')):
                output += run(
                    'ab %s %s | egrep "(^Failed)|(^Non-2xx)|(^Requests)"' %
                    (AB_FLAGS, TEST_URL)
                    )
                output += '\n'
                time.sleep(1)
        
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
                env.results.append(float(re.sub('[^0-9.]', '', line)))
        
        # Get the median of all results
        result = _median(env.results)
        
        # Update the results file
        env.resultsfp.seek(0)
        results_data = pickle.loads(env.resultsfp.read())
        
        if env.command not in results_data:
            results_data[env.command] = dict()
        if current_instance.id not in results_data[env.command]:
            results_data[env.command][current_instance.id] = dict()
        
        results_data[env.command][current_instance.id]['hello'] = result
        results_data[env.command][current_instance.id]['tmpl'] = 'n/a'
        results_data[env.command][current_instance.id]['db'] = 'n/a'
        env.resultsfp.seek(0)
        env.resultsfp.write(pickle.dumps(results_data))
        env.resultsfp.truncate()
    
    except Exception, e:
        print '*' * 80
        print '*%s*' % 'ABORTING DUE TO RUNTIME ERROR'.center(78)
        print '*' * 80
        
        raise e


@task
@parallel
def nodejs(run_tests=True):
    """Run the node.js control test."""
    INSTALL = 'python-software-properties dtach apache2-utils'
    TEST_URL = 'http://localhost:8000/'
    
    # Check the correct usage
    if sys.argv[1] != 'test':
        print '\nERROR: You must run "test" as the first task. Run "fab -l" ' \
              'for more information and a complete list of tasks.\n'
        sys.exit(1)
    
    # Get current instance info
    for instance in env.instances:
        if instance.public_dns_name == env.host:
            current_instance = instance
    try:
        if exists('/usr/bin/nodejs') and exists('/usr/bin/dtach'):
            pass
        else:
            # Do installs
            with settings(hide('running', 'stdout')):
                sudo('apt-get -y install ' + INSTALL)
                sudo('add-apt-repository ppa:chris-lea/node.js')
                sudo('apt-get update')
                sudo('apt-get -y install nodejs nodejs-dev')
        
        if run_tests is False:
            return
        
        # Setup test environment
        with settings(hide('running', 'stdout')):
            put(os.path.join(here, 'control_tests', 'nodejs'), '/home/ubuntu/')
            # For good measure
            sudo('chmod -R 777 /home/ubuntu/nodejs/')
            # Kill the last instance of nodejs before running it again
            run('pid=$(ps aux | sort -r | grep -v grep | grep -m 1 nodejs | ' \
                'awk \'{print $2}\'); if [ $pid ]; then kill -9 $pid; fi')
            run('dtach -n /tmp/nodejs -Ez nodejs /home/ubuntu/nodejs/node.js')
            time.sleep(1)
        
        with settings(hide('running', 'stdout')):
            if run('curl %s' % TEST_URL) != "Hello World!":
                print '*' * 80
                print '*%s*' % 'INVALID WEBSERVER RESPONSE'.center(78)
                print '*' * 80
                
                raise
        
        output = ''
        for i in range(NUM_AB_TESTS):
            with settings(hide('running', 'stdout')):
                output += run(
                    'ab %s %s | egrep "(^Failed)|(^Non-2xx)|(^Requests)"' %
                    (AB_FLAGS, TEST_URL)
                    )
                output += '\n'
                time.sleep(1)
        
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
                env.results.append(float(re.sub('[^0-9.]', '', line)))
        
        # Get the median of all results
        result = _median(env.results)
        
        # Update the results file
        env.resultsfp.seek(0)
        results_data = pickle.loads(env.resultsfp.read())
        
        if env.command not in results_data:
            results_data[env.command] = dict()
        if current_instance.id not in results_data[env.command]:
            results_data[env.command][current_instance.id] = dict()
        
        results_data[env.command][current_instance.id]['hello'] = result
        results_data[env.command][current_instance.id]['tmpl'] = 'n/a'
        results_data[env.command][current_instance.id]['db'] = 'n/a'
        env.resultsfp.seek(0)
        env.resultsfp.write(pickle.dumps(results_data))
        env.resultsfp.truncate()
    
    except Exception, e:
        print '*' * 80
        print '*%s*' % 'ABORTING DUE TO RUNTIME ERROR'.center(78)
        print '*' * 80
        
        raise e
