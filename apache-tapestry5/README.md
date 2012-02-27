Tapestry 5.3.2 Implementation
====

Created by Howard M. Lewis Ship \<hlship@gmail.com\>

[Apache Tapestry](http://tapestry.apache.org) is a popular Java language, component-oriented
web framework that combines high-performance with terrific developer productivity. This kind
of simple demo does not demonstrate Tapestry to its strengths, but it should still have a good
showing here.

Running the Application
----

The application executes from this directory using Gradle:

    ./gradlew jettyRun
	
This assumes that JDK 1.6 is installed locally.  On first execution,
the `gradlew` (Gradle Wrapper) script will automatically download all
necessary dependencies to build and execute the application.

By default, the application is configured to respond to the URL:

    http://localhost:8080/apache-tapestry5/
    
The root Index page includes simple links to the other three demonstration
pages:

* http://localhost:8080/apache-tapestry5/index.text
* http://localhost:8080/apache-tapestry5/helloworldstatic
* http://localhost:8080/apache-tapestry5/helloworlddb

The application's behavior was copied, as much as possible, from the sinatra application.
This included copying the hello.db file.


	
	

