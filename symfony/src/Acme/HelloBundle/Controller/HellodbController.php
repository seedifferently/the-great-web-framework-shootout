<?php

namespace Acme\HelloBundle\Controller;

use Symfony\Bundle\FrameworkBundle\Controller\Controller;


class HellodbController extends Controller
{
    
    public function indexAction()
    {
        $data = $this->getDoctrine()->getRepository('AcmeHelloBundle:Hello')->findAll();
        return $this->render('AcmeHelloBundle:Default:hellodb.html.twig', array('data' => $data));
    }
}
