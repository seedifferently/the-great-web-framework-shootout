<?php
return array
(
    'default' => array
    (
        'type'       => 'pdo',
        'connection' => array(
            'dsn' => 'sqlite:'.APPPATH.'hello.db',
            'persistent' => FALSE,
        ),
        'table_prefix' => '',
        'charset'      => NULL,
        'profiling'    => TRUE,
    )
);
?>
