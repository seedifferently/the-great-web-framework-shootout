package DancerDemo;
use Dancer ':syntax';
use Dancer::Plugin::Database;

our $VERSION = '0.1';

get '/' => sub {
    'Hello World';
};


get '/tt_hello' => sub {
    template 'tt_hello';
};


get '/db_hello' => sub {
    my @data = database->quick_select('hello', {}, {
        order_by => 'id asc',
        columns  => [qw(id data)]
    });

    template 'db_hello', { data => \@data };
};


true;
