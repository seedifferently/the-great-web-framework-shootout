package Hello::Controller::Root;
use Moose;
use namespace::autoclean;

BEGIN { extends 'Catalyst::Controller' }

__PACKAGE__->config(namespace => '');

sub hello :Path('/hello') :Args(0) {
    my $self = shift;
    my ($c) = @_;

    $c->response->body('Hello world');
}

sub hello_tt :Path('/hello_tt') :Args(0) { }

sub hello_db :Path('/hello_db') :Args(0) {
    my $self = shift;
    my ($c) = @_;

    my @hello = $c->model('SQLite')->resultset('Hello')->search({})->all;

    $c->stash->{data} = \@hello;
}

sub end : ActionClass('RenderView') {}

__PACKAGE__->meta->make_immutable;

1;
