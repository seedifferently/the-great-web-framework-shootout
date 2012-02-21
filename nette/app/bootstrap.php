<?php

/**
 * My Application bootstrap file.
 */
use Nette\Application\Routers\Route;


// Load Nette Framework
require LIBS_DIR . '/Nette/loader.php';


// Configure application
$configurator = new Nette\Config\Configurator;

// Enable Nette Debugger for error visualisation & logging
$configurator->setProductionMode(TRUE);
$configurator->enableDebugger(__DIR__ . '/../log');

// Enable RobotLoader - this will load all classes automatically
$configurator->setTempDirectory(__DIR__ . '/../temp');
$configurator->createRobotLoader()
	->addDirectory(APP_DIR)
	->addDirectory(LIBS_DIR)
	->register();

// Create Dependency Injection container from config.neon file
$configurator->addConfig(__DIR__ . '/config/config.neon', FALSE);
$container = $configurator->createContainer();

// Setup router
$container->router[] = new Route('index.php', 'Hello:default', Route::ONE_WAY);
if (!isset($container->parameters['stringController']) || !$container->parameters['stringController']) {
	$container->router[] = new Route('[hello]', function() {
		return new \Nette\Application\Responses\TextResponse('Hello Worlds!');
	});
}
$container->router[] = new Route('<presenter>/<action>[/<id>]', 'Hello:default');


// Configure and run the application!
$container->application->run();
