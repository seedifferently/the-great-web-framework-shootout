<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">
  
  <head>
    <title>Hello World</title>
  </head>

    <body>
    <?php
        if ($page == 'hellos') {
            echo View::factory('hellos')->render();
        }
        else if ($page == 'hellodb') {
            echo View::factory('hellodb', array('data' => $data))->render();
        }
        else if ($page == 'helloorm') {
            echo View::factory('helloorm', array('data' => $data))->render();
        }
    ?>
    </body>

</html>
