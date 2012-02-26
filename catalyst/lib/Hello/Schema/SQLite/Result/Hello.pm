package Hello::Schema::SQLite::Result::Hello;
use strict;
use warnings;

use base 'DBIx::Class::Core';

__PACKAGE__->table('hellos');

__PACKAGE__->add_columns(
    'id',
    { datatype => 'integer', is_nullable => 0 },
    'data',
    { datatype => 'varchar' },
);
__PACKAGE__->set_primary_key('id');

1;
