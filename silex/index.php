<?php

/**
 * This is the main application which sets up the routing for silex
 *
 * @author Markus Tacker <m@coderbyheart.de>
 */

/**
 * Include required libs
 */
require_once __DIR__ . '/vendor/silex-2012-02-20.phar';

$app = new Silex\Application();
$app['debug'] = true;

// Register extra module for the templating engine
$app->register(new Silex\Provider\TwigServiceProvider(), array(
    'twig.path' => __DIR__ . '/templates',
    'twig.class_path' => __DIR__ . '/vendor/twig-1.6.0/lib',
));

// Now for the routes

// Plaintext response
$app->get('/hello', function() use($app)
{
    return 'Hello World!';
});

// Template-Response
$app->get('/twig_hello', function() use($app)
{
    return $app['twig']->render('hello.html.twig');
});

// DB-Response
$app->get('/twig_hellodb', function() use($app)
{
    $pdo = new PDO('sqlite:///' . __DIR__ . '/hello.db');
    $result = $pdo->query('SELECT * FROM hello');
    $data = array();
    while ($row = $result->fetch()) {
        $data[] = $row;
    }
    $result->closeCursor();
    return $app['twig']->render('hellodb.html.twig', array('data' => array()));
});

// Done.
$app->run();
