<?php

class HellodbPresenter extends \Nette\Application\UI\Presenter
{

	public function renderDefault()
	{
		$this->template->data = $this->getContext()->database->table('hello');
	}

}
