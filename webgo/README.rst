================================================================================
Web.go test code for The Great Web Framework Shootout
================================================================================

| Copyright: (c) 2012 Seth Davis
| http://blog.curiasolutions.com/the-great-web-framework-shootout/


Synopsis
--------------------------------------------------------------------------------

This code was last tested using Web.go **commit 111463f** for **Go r59** and
will likely perform differently when using a different version.


Benchmark Results
--------------------------------------------------------------------------------

Note: These tests were run using Go's own built-in server. Also, and I'm only
casually familiar with Go, so if somebody could add a SQLite test to the test
app I’d be extremely grateful.


=============        ========
Test                 Reqs/sec
=============        ========
Hello World              3346
Template                 1959
Template & DB             n/a
=============        ========


Please see `The Great Web Framework Shootout`_ website for more information.

.. _The Great Web Framework Shootout:
   http://blog.curiasolutions.com/the-great-web-framework-shootout/
