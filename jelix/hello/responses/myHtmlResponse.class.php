<?php
/**
* @package   hello
* @subpackage 
* @author    Olivier Demah
* @copyright 2011 Olivier Demah
* @link      http://www.foxmask.info
* @license   http://gnu.org All rights reserved
*/


require_once (JELIX_LIB_CORE_PATH.'response/jResponseHtml.class.php');

class myHtmlResponse extends jResponseHtml {

    public $bodyTpl = 'hello~main';

    function __construct() {
        parent::__construct();

        // Include your common CSS and JS files here
    }

    protected function doAfterActions() {
        // Include all process in common for all actions, like the settings of the
        // main template, the settings of the response etc..

        $this->body->assignIfNone('MAIN','<p>no content</p>');
    }
}
