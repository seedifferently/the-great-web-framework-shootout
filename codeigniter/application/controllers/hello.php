<?php if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class Hello extends CI_Controller {

	public function index()
	{
		echo 'Hello World!';
	}
	
	public function hellos()
	{
		$this->load->view('hellos');
	}
	
	function hellodb()
	{
		$this->load->database();
		$data['data'] = $this->db->get('hello');
		$this->load->view('hellodb', $data);
	}
}
