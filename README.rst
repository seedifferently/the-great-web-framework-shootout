================================================================================
The Great Web Framework Shootout
================================================================================

| Copyright: (c) 2012 Seth Davis
| http://blog.curiasolutions.com/the-great-web-framework-shootout/


**WARNING: YOU ARE CURRENTLY VIEWING THE DEV BRANCH WHICH IS A WORK IN PROGRESS
BRANCH AND LIKELY CONTAINS INACCURATE AND/OR INCOMPLETE DATA!**


Synopsis
================================================================================

Welcome to the great web framework shootout. Here you will find test code and
benchmark results comparing the performance of a few of the most popular F/OSS
web frameworks in use today.

Please see `The Great Web Framework Shootout`_ website for important disclaimers
and other detailed information about these benchmarks. If you have any questions
or comments, feel free to contact me on `Google+`_.

.. _The Great Web Framework Shootout:
   http://blog.curiasolutions.com/the-great-web-framework-shootout/
.. _Google+: http://profiles.google.com/seedifferently


Frequently Asked Questions *(please read before creating an issue)*
================================================================================

Do these results have any real world value?
--------------------------------------------------------------------------------

Probably not. When it comes to code, the slightest adjustments have the
potential to change things drastically. While I have tried to perform each test
as fairly and accurately as possible, it would be foolish to consider these
results as scientific in any way. It should also be noted that my goal here was
not necessarily to figure out how fast each framework could perform at its *most
optimized* configuration (although built-in caching and other performance tweaks
were usually enabled if the default configuration permitted it), but rather to
see what a *minimal "out-of-the-box" experience* would look like.

Additionally, nothing here is intended to make one web technology appear
"better" than another. When it comes to using the right tool for the job,
"faster" does not necessarily mean "better" (very few real world projects are
going to depend solely on page request speeds).


Will you please add XYZ to the results?
--------------------------------------------------------------------------------

Maybe, if you can convince me that enough people would be interested in having
it displayed next to heavyweights like Rails and Django. Fork the repository
and submit a pull request *under the dev branch* with a test app in the same
format as the other tests, and make sure you include your best sales pitch.
Otherwise, I'd suggest you boot up the EC2 AMI and do your own benchmarking.


What kind of test setup are you using?
--------------------------------------------------------------------------------

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

The three basic tests that each framework was set up to run were:

1. The "Hello World" test: This test simply spits out a string response. There's
   no template or DB calls involved, so the level of processing should be
   minimal.
2. The template test: This test prints out Lorem Ipsum via a template (thus
   engaging the framework's templating systems).
3. The template/db test: This test loads 5 rows of Lorem Ipsum from a SQLite DB
   (via the default ORM or a sqlite3 driver) and then prints them out through a
   template (thus engaging both the framework's ORM/DB driver and the templating
   system).


Benchmark Results
================================================================================

The benchmark results can be viewed in the README.rst file in each framework's
test code directory. For the complete report, please see `The Great Web
Framework Shootout`_ website where you will find a better breakdown of the tests
(including side-by-side graphs).

.. _The Great Web Framework Shootout:
   http://blog.curiasolutions.com/the-great-web-framework-shootout/


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
