<?php

namespace Acme\HelloBundle\Controller;

use Symfony\Bundle\FrameworkBundle\Controller\Controller;


class HelloController extends Controller
{
    
    public function indexAction()
    {
        return $this->render('AcmeHelloBundle:Default:hello.html.twig'); # return $this->render('AcmeHelloBundle:Default:index.html.twig', array('name' => $name));
    }
}
