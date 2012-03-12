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
def nodejs():
    """Run the express nodejs test."""
    INSTALL = 'build-essential libsqlite3-dev'
    HELLO_TEST_URL = 'http://localhost:8000/'
    TMPL_TEST_URL = 'http://localhost:8000/hb_hello'
    DB_TEST_URL = 'http://localhost:8000/hb_sql'
    
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
        if exists('/usr/bin/nodejs') and exists('/usr/bin/npm') and \
           exists('/usr/bin/dtach'):
            # Kill nodejs before running it again
            if int(run('ps aux | grep -c nodejs')) > 2:
                sudo('killall -9 nodejs')
        else:
            # Check requirements
            if not exists('/usr/bin/nodejs'):
                print '\nERROR: Required dependencies have not yet been ' \
                      'installed. Please run the "nodejs" task at least once ' \
                      'before running this task.\n'
                sys.exit(1)
            elif not exists('/usr/bin/npm'):
                sudo('curl http://npmjs.org/install.sh | sh')
            
            # Do installs
            sudo('apt-get -y install ' + INSTALL)
    
        # Setup test environment
        put(here, '/home/ubuntu/')
        with cd('/home/ubuntu/express/'):
            # Install dependencies
            run('npm install')
        # For good measure
        sudo('chmod -R 777 /home/ubuntu/express/')
        run('dtach -n /tmp/express -Ez nodejs '
            '/home/ubuntu/express/express_app.js')
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
        sudo('killall -9 nodejs')
    
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
