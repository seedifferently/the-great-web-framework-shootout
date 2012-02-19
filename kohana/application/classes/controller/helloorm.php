<?php defined('SYSPATH') or die('No direct script access.');

class Controller_Helloorm extends Controller_Template {

	public $template = 'helloorm';

	# COULD NOT GET THIS WORKING WITH SQLITE FOR SOME REASON!
	public function action_index()
	{
		$hello = new Model_Hello();
		$data = $hello->find_all();
		
		$this->template->title = 'Hello World';
		$this->template->data = $data;
	}

} // End Welcome
