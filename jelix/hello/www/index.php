<?php
/**
* @package   hello
* @subpackage 
* @author    Olivier Demah
* @copyright 2011 Olivier Demah
* @link      http://www.foxmask.info
* @license   http://gnu.org All rights reserved
*/

require ('../application.init.php');
require (JELIX_LIB_CORE_PATH.'request/jClassicRequest.class.php');

checkAppOpened();

$config_file = 'index/config.ini.php';

$jelix = new jCoordinator($config_file);
$jelix->process(new jClassicRequest());


