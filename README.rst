================================================================================
The Great Web Framework Shootout
================================================================================

| Copyright: (c) 2012 Seth Davis
| http://blog.curiasolutions.com/the-great-web-framework-shootout/


Synopsis
================================================================================

Welcome to the great web framework shootout. Here you will find test code and
benchmark results comparing the performance of a few of the most popular F/OSS
web frameworks in use today.

Please see `The Great Web Framework Shootout's website`_ for disclaimers, pretty
little graphs, and other important information.

.. _The Great Web Framework Shootout's website:
   http://blog.curiasolutions.com/the-great-web-framework-shootout/


Will you please add XYZ to the results?
================================================================================

Maybe, if you can convince me that enough people would be interested in having
it displayed next to heavyweights like Rails and Django. Fork the repository and
submit a pull request with the test app code and your best sales pitch.
Otherwise, I'd suggest you boot up the EC2 AMI and do your own benchmarking.


Benchmark Results
================================================================================

Three basic tests were set up for each framework up to run. Below are the
results of each test in requests per second from highest (best performance) to
lowest (worst performance).


The "Hello World" String Test
--------------------------------------------------------------------------------

This test simply spits out a string response. There's no template or DB calls
involved, so the level of processing should be minimal.

=================        ========
Framework                Reqs/sec
=================        ========
web.go (Go r59)              3346
Pyramid 1.2                  3026
Bottle 0.9.6                 2825
Django 1.3.1                 2159
Flask 0.7.2                  2054
Sinatra 1.2.6                1583
CodeIgniter 2.0.3             929
TG 2.1.2                      839
Yii 1.1.8                     726
Kohana 3.2.0                  714
Rails 3.1                     711
Symfony 2.0.1                 273
CakePHP 1.3.11                254
=================        ========


The "Hello World" Template Test
--------------------------------------------------------------------------------

This test prints out Lorem Ipsum via a template (thus engaging the framework's
templating systems).

=================        ========
Framework                Reqs/sec
=================        ========
Bottle 0.9.6                 2417
web.go (Go r59)              1959
Flask 0.7.2                  1918
Pyramid 1.2                  1650
Sinatra 1.2.6                1329
Django 1.3.1                 1005
CodeIgniter 2.0.3             884
Kohana 3.2.0                  675
TG 2.1.2                      663
Rails 3.1                     625
Yii 1.1.8                     548
CakePHP 1.3.11                203
Symfony 2.0.1                 171
=================        ========


The "Hello World" Template Test With DB Query
--------------------------------------------------------------------------------

This test loads 5 rows of Lorem Ipsum from a SQLite DB (via the default ORM or
a sqlite3 driver) and then prints them out through a template (thus engaging
both the framework’s ORM/DB driver and the templating system).

=================        ========
Framework                Reqs/sec
=================        ========
Bottle 0.9.6                 1562
Flask 0.7.2                  1191
Sinatra 1.2.6                 982
web.go (Go r59)               741
Pyramid 1.2                   555
CodeIgniter 2.0.3             542
Django 1.3.1                  465
Rails 3.1                     463
Kohana 3.2.0                  423
TG 2.1.2                      298
Yii 1.1.8                     201
CakePHP 1.3.11                193
Symfony 2.0.1                 113
=================        ========


Test Platform Setup
================================================================================

All tests were performed on Amazon's EC2 with the following configuration:

* ami-fbbf7892 m1.large ubuntu-images-us/ubuntu-lucid-10.04-amd64-server-
  20110719.manifest.xml
* As a "Large" instance, Amazon describes the resources as: 7.5 GB of memory, 4
  EC2 Compute Units (2 virtual cores with 2 EC2 Compute Units each), 850 GB of
  local instance storage, 64-bit platform.
* Apache 2.2.14 was used. (Yes, I know there are other options, but with
  Apache's market share I figured it would be a good baseline.)
* Python 2.6.5 and mod_wsgi 2.8 (embedded mode) were used for the Python based
  tests.
* Ruby 1.9.2p290 and Phusion Passenger 3.0.9 were used for the Ruby based tests.
* PHP 5.3.2 (with APC enabled) was used for the PHP based tests.
* ApacheBench was run with -n 10000 and -c 10 about 5-10 times each, and the
  "best guess average" was chosen.


Most Recent Changes
================================================================================

09/12/2011
--------------------------------------------------------------------------------

* Updated Ubuntu LTS AMI (ami-fbbf7892 ubuntu-images-us/ubuntu-lucid-10.04-
  amd64-server-20110719.manifest.xml)
* Rails 2.x and 3.0 were dropped in favor of Rails 3.1.
* CakePHP 1.2 was dropped in favor of 1.3, but Symfony and Yii were added as
  they seem to have considerable market share.
* Corrected faulty configuration of CakePHP's caching engine.

See `CHANGELOG.rst`_ for more.

.. _CHANGELOG.rst: http://github.com/seedifferently/the-great-web-framework-
                   shootout/blob/master/CHANGELOG.rst
