#!/usr/bin/env perl
# IMPORTANT: if you delete this file your app will not work as
# expected.  You have been warned.
use inc::Module::Install 1.02;
use Module::Install::Catalyst; # Complain loudly if you don't have
                               # Catalyst::Devel installed or haven't said
                               # 'make dist' to create a standalone tarball.

name 'Hello';
all_from 'lib/Hello.pm';

requires 'Catalyst::Runtime' => '5.90010';
requires 'Catalyst::Action::RenderView';
requires 'Catalyst::View::TT';
requires 'Catalyst::Model::DBIC::Schema';
requires 'Moose';
requires 'namespace::autoclean';
catalyst;

install_script glob('script/*.pl');
auto_install;
WriteAll;
