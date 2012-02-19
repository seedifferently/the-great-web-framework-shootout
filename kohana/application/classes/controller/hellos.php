<?php defined('SYSPATH') or die('No direct script access.');

class Controller_Hellos extends Controller_Template {

	public $template = 'hellos';

	public function action_index()
	{
		// Set the page title
		$this->template->title = 'Hello World';
	}

} // End Welcome
