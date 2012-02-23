package Hello;
use Moose;
use namespace::autoclean;

use Catalyst::Runtime 5.90;

use Catalyst;

extends 'Catalyst';

our $VERSION = '0.01';

__PACKAGE__->config(
    name                                        => 'Hello',
    disable_component_resolution_regex_fallback => 1,
    enable_catalyst_header                      => 1,
    'View::TT'                                  => {
        TEMPLATE_EXTENSION => '.tt',
        DEFAULT_ENCODING   => 'utf-8',
        INCLUDE_PATH       => [ __PACKAGE__->path_to('root', 'template') ],
    },
    'Model::SQLite'                             => { },
);

__PACKAGE__->setup();

1;
