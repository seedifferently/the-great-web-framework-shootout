package Hello::Model::SQLite;
use Moose;

extends 'Catalyst::Model::DBIC::Schema';

__PACKAGE__->config(
    schema_class => 'Hello::Schema::SQLite',
    connect_info => [ 'dbi:SQLite:hello.sqlite3', '', '' ],
);

no Moose;

1;
