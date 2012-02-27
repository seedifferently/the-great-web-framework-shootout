Tapestry 5.3.2 implementation
====

Created by Howard M. Lewis Ship <hlship@gmail.com>

Running the Application
----

The application executes from this directory using Gradle:

    ./gradlew jettyRun
	
This assumes that JDK 1.6 is installed locally.  On first execution,
the `gradlew` (Gradle Wrapper) script will automatically download all
necessary dependencies to build and execute the appliation.

By default, the application is configured to respond to the URL:

    http://localhost:8080/t5app
	
	

