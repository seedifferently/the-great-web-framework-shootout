<?php

class HellodbController extends Controller
{
	public function actionIndex()
	{
		$data = Hello::model()->findAll();
		$this->render('index', array('data' => $data));
	}
}
