<?php
/**
* @package   hello
* @subpackage hello
* @author    Olivier Demah
* @copyright 2011 Olivier Demah
* @link      http://www.foxmask.info
* @license   http://gnu.org All rights reserved
*/


class helloModuleInstaller extends jInstallerModule {

    function install() {
        //if ($this->firstDbExec())
        //    $this->execSQLScript('sql/install');

        /*if ($this->firstExec('acl2')) {
            jAcl2DbManager::addSubject('my.subject', 'hello~acl.my.subject', 'subject.group.id');
            jAcl2DbManager::addRight('admins', 'my.subject'); // for admin group
        }
        */
    }
}