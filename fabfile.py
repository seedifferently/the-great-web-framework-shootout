"""
================================================================================
Benchmark test runner for The Great Web Framework Shootout.
================================================================================

Usage: fab test <test task(s)> cleanup

Test configuration can be modified inside the fabfile.py. Alternatively, you can
specify ApacheBench options via the "test" task using Fabric's kwargs passing
syntax.

Example: fab test:num_ab_tests=5,ab_flags="-q -c 100 -t 5" apache nodejs cleanup


Type "fab -l" for a full list of tasks.


THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHOR BE
LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import sys, os, time, inspect, re, tempfile, pickle
from fabric.state import env
from fabric.decorators import task, parallel, serial
from fabric.operations import put, run, sudo
from fabric.context_managers import cd, hide, settings
from fabric.contrib.files import exists
from boto import ec2

from control_tests.apache import apache
from control_tests.gohttp import gohttp
from control_tests.nodejs import nodejs
from control_tests import perl, php, python, ruby
import sinatra


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
AB_FLAGS = '-q -c 10 -n 10000' # apachebench flags to use



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
def test(num_ab_tests=NUM_AB_TESTS, ab_flags=AB_FLAGS):
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
    env.NUM_AB_TESTS = int(num_ab_tests)
    env.AB_FLAGS = ab_flags
    env.user = 'ubuntu'
    env.hosts = []
    env.results = dict(hello=[], tmpl=[], db=[])
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
                      'be running. Please check your USE_EC2_INSTANCES ' \
                      'settings.\n'
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
    if env.host == env.hosts[-1]:
        try:
            # Terminate instances if needed
            if TERMINATE_INSTANCES and hasattr(env.instances[0], 'state'):
                instances = [instance.id for instance in env.instances]
            else:
                instances = None
            
            if instances:
                conn.terminate_instances(instances)
        except Exception, e:
            print '*' * 80
            print '*%s*' % 'UNABLE TO TERMINATE INSTANCES'.center(78)
            print '*' * 80
            print e
        
        
        # Load the results data
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
