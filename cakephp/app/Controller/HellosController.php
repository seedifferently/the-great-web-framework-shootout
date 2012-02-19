<?php
App::uses('AppController', 'Controller');

class HellosController extends AppController {

	public $name = 'Hellos';
	public $uses = array('Hello');

	// index action: default view
	public function index() {
		echo "Hello World!";
		exit;
	}

	public function hellos() {
		#
	}

	public function hellodb() {
		$this->set('data', $this->Hello->find('all'));
	}
}