<?php

class Controller_Hellodb extends Controller_Template
{
	public $template = 'hellodb';

	public function action_index()
	{
		$this->template->set('data', DB::select()->from('hello')->as_object()->execute(), false);
	}

}