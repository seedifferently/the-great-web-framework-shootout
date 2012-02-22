<?php
/**
* @package   hello
* @subpackage
* @author    Olivier Demah
* @copyright 2011 Olivier Demah
* @link      http://www.foxmask.info
* @license   http://gnu.org All rights reserved
*/

$appPath = dirname (__FILE__).'/';
require (realpath($appPath.'../lib/jelix/').'/'.'init.php');

jApp::initPaths(
    $appPath,
    $appPath.'www/',
    $appPath.'var/',
    $appPath.'var/log/',
    $appPath.'var/config/',
    $appPath.'scripts/'
);
jApp::setTempBasePath(realpath($appPath.'../temp/hello/').'/');
