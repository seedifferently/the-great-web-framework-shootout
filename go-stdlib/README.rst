================================================================================
Go test code for The Great Web Framework Shootout
================================================================================

| Copyright: (c) 2012 Andrew Gerrand


Synopsis
================================================================================

An implementation of the 'webgo' benchmark that uses Go's built-in net/http and
html/template pacakges instead of web.go and mustache.go. This implementation
also provides a database example using the built-in database/sql abstraction
layer and mattn's go-sqlite3.

Go's http and template packages are more mature and featureful than the libraries
orignally chosen for the shootout.

This was written to run against Go version weekly.2012-02-14.
