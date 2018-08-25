#!/usr/local/cpanel/3rdparty/bin/perl

# cpanel - t/SOURCES-cpanel-scripts-ea-tomcat85.t    Copyright 2018 cPanel, Inc.
#                                                           All rights Reserved.
# copyright@cpanel.net                                         http://cpanel.net
# This code is subject to the cPanel license. Unauthorized copying is prohibited

## no critic qw(TestingAndDebugging::RequireUseStrict TestingAndDebugging::RequireUseWarnings)
use Test::Spec;    # automatically turns on strict and warnings

use FindBin;
use Path::Tiny;
use XML::LibXML;

our $system_calls   = [];
our $current_system = sub {
    push @{$system_calls}, [@_];
    if ( $_[0] =~ m/port_auth/ ) { print "10000\n10001\n10002\nnon port msg\n\n"; }
    elsif ( $_[0] =~ qr/^cp / || $_[0] =~ m/^chmod / ) { goto &Test::Mock::Cmd::orig_system }
    return 0;
};
use Test::Mock::Cmd 'system' => sub { $current_system->(@_) };

my %conf = (
    require => "$FindBin::Bin/../SOURCES/cpanel-scripts-ea-tomcat85",
    package => "scripts::ea_tomcat85",
);
require $conf{require};
require '/usr/local/cpanel/scripts/cpuser_service_manager';
require '/usr/local/cpanel/scripts/cpuser_port_authority';

spec_helper "/usr/local/cpanel/t/small/.spec_helpers/App-CmdDispatch_based_modulinos.pl";

describe "private tomcat manager script" => sub {
    share my %mi;
    around {
        local $ENV{"scripts::ea_tomcat85::bail_die"} = 1;

        $conf{_homedir} = Path::Tiny->tempdir();
        no warnings "redefine", "once";
        local *Cpanel::Config::LoadUserDomains::loaduserdomains = sub { "user$$" => [], "us3r$$" => [], };
        local *scripts::cpuser_service_manager::_get_homedir    = sub { $conf{_homedir} };
        local *scripts::ea_tomcat85::_get_homedir               = sub { $conf{_homedir} };
        local *Cpanel::AccessIds::do_as_user                    = sub { shift; shift->() };
        local $scripts::cpuser_port_authority::port_authority_conf = "$conf{_homedir}/pa_conf.json";
        use warnings "redefine", "once";

        %mi = %conf;
        yield;
    };

    before each => sub { @{$system_calls} = () };

    it_should_behave_like "all App::CmdDispatch modulino scripts";

    it_should_behave_like "all App::CmdDispatch scripts w/ help";

    describe "sub-command" => sub {

        # sad args
        it "`add` missing user should error out" => sub {
            modulino_run_trap("add");
            is $trap->{die}, "User argument is missing.\n";
        };

        it "`add <NON-USER>` should error out" => sub {
            modulino_run_trap( add => "derp" );
            is $trap->{die}, "User argument is invalid.\n";
        };

        it "`rem` missing user should error out" => sub {
            modulino_run_trap("rem");
            is $trap->{die}, "User argument is missing.\n";
        };

        it "`rem <NON-USER>` should error out" => sub {
            modulino_run_trap( rem => "derp" );
            is $trap->{die}, "User argument is invalid.\n";
        };

        it "`rem <USER>` without --verify should error out" => sub {
            mkdir "$mi{_homedir}/ea-tomcat85";
            modulino_run_trap( rem => "user$$" );
            rmdir "$mi{_homedir}/ea-tomcat85";
            like $trap->{die}, qr/--verify/;
        };

        it "`rem <USER>` with --verify should error out" => sub {
            mkdir "$mi{_homedir}/ea-tomcat85";
            modulino_run_trap( rem => "user$$", "--verify" );
            rmdir "$mi{_homedir}/ea-tomcat85";
            like $trap->{die}, qr/--verify/;
        };

        it "`rem <USER>` with --verify= should error out" => sub {
            mkdir "$mi{_homedir}/ea-tomcat85";
            modulino_run_trap( rem => "user$$", "--verify=" );
            rmdir "$mi{_homedir}/ea-tomcat85";
            like $trap->{die}, qr/--verify/;
        };

        it "`rem <USER>` with --verify=NOT-USER should error out" => sub {
            mkdir "$mi{_homedir}/ea-tomcat85";
            modulino_run_trap( rem => "user$$", "--verify=derp" );
            rmdir "$mi{_homedir}/ea-tomcat85";
            like $trap->{die}, qr/--verify/;
        };

        # happy path
        it "`add <USER>` should create ~/ea-tomcat85/" => sub {
            modulino_run_trap( add => "user$$" );
            ok -d "$mi{_homedir}/ea-tomcat85";
        };

        it "`add <USER>` should get ports" => sub {
            modulino_run_trap( add => "user$$" );
            is_deeply $system_calls->[0], [ '/usr/local/cpanel/scripts/cpuser_port_authority', 'give', "user$$", 3, '--service=ea-tomcat85' ];
        };

        it "`add <USER>` should setup service" => sub {
            modulino_run_trap( add => "user$$" );
            is_deeply $system_calls->[3], [qw(/usr/local/cpanel/scripts/cpuser_service_manager add ea-tomcat85 --init-script=/opt/cpanel/ea-tomcat85/bin/user-init.sh)];
        };

        it "`add <USER>` should start tomcat" => sub {
            modulino_run_trap( add => "user$$" );
            is_deeply $system_calls->[4], [qw(ubic start ea-tomcat85)];
        };

        it "`add <USER>` should configure ports in server.xml" => sub {
            modulino_run_trap( add => "user$$" );
            my $dom = XML::LibXML->load_xml( location => "$mi{_homedir}/ea-tomcat85/conf/server.xml" );
            my %res;
            ( $res{shutdown_port} ) = $dom->findnodes('//Server[@shutdown="SHUTDOWN"]')->shift()->getAttribute("port");

            for my $conn ( $dom->findnodes("//Server/Service/Connector") ) {
                if ( $conn->getAttribute('protocol') eq 'HTTP/1.1' ) {
                    $res{http_port}          = $conn->getAttribute("port");
                    $res{http_redirect_port} = $conn->getAttribute("redirectPort");
                }
                elsif ( $conn->getAttribute('protocol') eq 'AJP/1.3' ) {
                    $res{ajp_port}          = $conn->getAttribute("port");
                    $res{ajp_redirect_port} = $conn->getAttribute("redirectPort");
                }
            }

            is_deeply \%res, { shutdown_port => -1, http_port => 10000, http_redirect_port => 10002, ajp_port => 10001, ajp_redirect_port => 10002 };
        };

        it "`list` should error out when given extra arguments" => sub {
            modulino_run_trap( "list", "--derp" );
            is( $trap->{die}, "“list” does not take any arguments\n" );
        };

        it "`list` should list multiple users one per line" => sub {
            modulino_run_trap( add => "user$$" );
            modulino_run_trap( add => "us3r$$" );
            modulino_run_trap("list");
            like $trap->{stdout}, qr/us3r$$\nuser$$\n/;
        };

        it "`rem <USER> --verify=<USER>` should remove ~/ea-tomcat85" => sub {
            modulino_run_trap( add => "user$$" );
            modulino_run_trap( rem => "user$$", "--verify=user$$" );
            ok !-d "$mi{_homedir}/ea-tomcat85";
        };

        it "`rem <USER> --verify=<USER>` should stop tomcat" => sub {
            modulino_run_trap( add => "user$$" );
            @{$system_calls} = ();
            modulino_run_trap( rem => "user$$", "--verify=user$$" );
            is_deeply $system_calls->[-2], [qw(ubic stop ea-tomcat85)];
        };

        it "`rem <USER> --verify=<USER>` should remove service" => sub {
            modulino_run_trap( add => "user$$" );
            @{$system_calls} = ();
            modulino_run_trap( rem => "user$$", "--verify=user$$" );
            is_deeply $system_calls->[-1], [qw(/usr/local/cpanel/scripts/cpuser_service_manager rem ea-tomcat85)];
        };

        it "`add <USER>` should error out if user already has tomcat 8.5" => sub {
            mkdir "$mi{_homedir}/ea-tomcat85";
            modulino_run_trap( add => "user$$" );
            is $trap->{die}, "The user already has a tomcat 8.5 instance.\n";
        };

        it "`rem <USER> --verify=<USER>` should error out if user does not have tomcat" => sub {
            modulino_run_trap( rem => "user$$", "--verify='user$$'" );
            is $trap->{die}, "The user does not have a tomcat 8.5 instance.\n";
        };

        it "`remove` should be an alias for `rem`" => sub {
            modulino_run_trap( add => "user$$" );
            modulino_run_trap( "remove", "user$$", "--verify='user$$'" );
            is $trap->{stdout}, "Removing user$$’s tomcat 8.5 instance …\n";
        };

        it "`list` should list nothing when there are no tomcat users" => sub {
            modulino_run_trap("list");
            is( $trap->{stdout}, "" );
        };
    };
};

runtests unless caller;
