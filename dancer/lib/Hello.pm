package Hello;
use Dancer ':syntax';
use Dancer::Plugin::DBIC 'schema';

our $VERSION = '0.1';

set template => 'template_toolkit';
set layout   => 'main';
set plugins  => {
    'DBIC' => {
        default => { dsn => 'dbi:SQLite:hello.sqlite3' },
    },
};

get '/hello' => sub {
    'Hello world'
};

get '/hello_tt' => sub {
    template 'hello_tt';
};

get '/hello_db' => sub {
    my @data = schema->resultset('Hello')->search({})->all;
    template 'hello_db' => {
        data => \@data,
    };
};

true;
