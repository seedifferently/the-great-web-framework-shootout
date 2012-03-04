================================================================================
Changelog
================================================================================


04/XX/2012 (in development)
--------------------------------------------------------------------------------

* The test platform was updated to the latest Ubuntu 10.04 LTS AMI: ami-5c9b4935
* Added a fabfile.py script so that the tests can be automated using `Fabric`_.
* Added a "control tests" directory with plain "Hello World" tests for Apache,
  PHP (mod_php), Python (mod_wsgi), Ruby (mod_passenger), Perl (Plack/PSGI),
  JavaScript (node.js), and Go (Go's http package).

.. _Fabric: http://www.fabfile.org


09/12/2011
--------------------------------------------------------------------------------

* Updated Ubuntu LTS AMI (ami-fbbf7892 ubuntu-images-us/ubuntu-lucid-10.04-
  amd64-server-20110719.manifest.xml)
* Rails 2.x and 3.0 were dropped in favor of Rails 3.1.
* CakePHP 1.2 was dropped in favor of 1.3, but Symfony and Yii were added as
  they seem to have considerable market share.
* Corrected faulty configuration of CakePHP's caching engine.
