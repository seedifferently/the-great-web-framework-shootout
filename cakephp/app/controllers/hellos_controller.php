<?php
class HellosController extends AppController {

	var $name = 'Hellos';
	var $uses = 'Hello';

	// index action: default view
	function index() {
		echo "Hello World!";
		exit;
	}

	function hellos() {
		#
	}

	function hellodb() {
		$this->set('data', $this->Hello->find('all'));
	}
}
?>

