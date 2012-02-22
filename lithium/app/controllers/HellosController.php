<?php

namespace app\controllers;

use app\models\Hellos;

class HellosController extends \lithium\action\Controller {
	public function index() {
		echo "Hello World!";
		exit();
	}

	public function hellos() {
	}

	public function hellodb() {
		$hellos = Hellos::all();
		return compact('hellos');
	}
}

?>