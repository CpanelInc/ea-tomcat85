package Cpanel::ServiceManager::Services::Ea_tomcat85;

# cpanel - Cpanel/ServiceManager/Services/Ea_tomcat85.pm
#                                                    Copyright 2018 cPanel, Inc.
#                                                           All rights Reserved.
# copyright@cpanel.net                                         http://cpanel.net
# This code is subject to the cPanel license. Unauthorized copying is prohibited

use strict;
use warnings;

use Cpanel::Class;    #issafe #nomunge
use Cpanel::ServiceManager::Base ();

extends 'Cpanel::ServiceManager::Base';

has is_cpanel_service => ( default => 0 );
has pidfile           => ( default => '/var/run/catalina.pid' );
has ports             => ( default => sub { return [8080] } );

no Cpanel::Class;     #issafe #nomunge

1;
