<?php defined('SYSPATH') or die('No direct script access.');

class Controller_Hellodb extends Controller_Template {

	public $template = 'hellodb';

	public function action_index()
	{
		$data = DB::select()->from('hello')->execute()->as_array();
		
		$this->template->title = 'Hello World';
		$this->template->data = $data;
	}

} // End Welcome
