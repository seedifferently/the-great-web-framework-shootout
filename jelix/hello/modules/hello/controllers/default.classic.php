<?php
class defaultCtrl extends jController {
    function index() {
        $rep = $this->getResponse('text');
        $rep->content = 'Hello world';
        return $rep;
    }

    function hellos() {
        $rep = $this->getResponse('html');
	$tpl = new jTpl();
        $rep->body->assign('MAIN', $tpl->fetch('hellos'));
        return $rep;
    }

    function hellodb() {
        $rep = $this->getResponse('html');
	$c = jDb::getConnection();
	$tpl = new jTpl();
	$tpl->assign('data',$c->query('SELECT id,data FROM '.$c->prefixTable('hello')));
        $rep->body->assign('MAIN', $tpl->fetch('hellodb'));
        return $rep;
    }
}
