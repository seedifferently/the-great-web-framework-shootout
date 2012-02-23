use strict;
use warnings;

use Hello;

my $app = Hello->apply_default_middlewares(Hello->psgi_app);
$app;

