<?php

namespace Acme\HelloBundle\Controller;

use Symfony\Component\HttpFoundation\Response;


class DefaultController
{
    
    public function indexAction()
    {
        return new Response('Hello World!');
    }
    
#    public function helloAction()
#    {
#        return $this->render('AcmeHelloBundle:Default:hello.html.twig'); # return $this->render('AcmeHelloBundle:Default:index.html.twig', array('name' => $name));
#    }
}
