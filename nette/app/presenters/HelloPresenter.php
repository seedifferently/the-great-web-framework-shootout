<?php

class HelloPresenter extends \Nette\Application\UI\Presenter
{

	public function actionDefault()
	{
		$this->sendResponse(new \Nette\Application\Responses\TextResponse('Hello World!'));
	}

}
