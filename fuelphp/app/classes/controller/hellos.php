<?php

class Controller_Hellos extends Controller
{

	public function action_index()
	{
		echo View::forge('hello');
	}

}
