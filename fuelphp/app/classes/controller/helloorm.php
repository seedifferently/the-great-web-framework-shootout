<?php

class Controller_Helloorm extends Controller_Template {
	
	public $template = 'hellodb';
	
	public function action_index()
	{
		Package::load('orm');	
		$this->template->set('data', Model_Hello::find('all'), false);
	}
}