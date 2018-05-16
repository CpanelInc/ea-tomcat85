# cpanel - t/SOURCES-cpanel-scripts-ea-tomcat85.t    Copyright 2018 cPanel, Inc.
#                                                           All rights Reserved.
# copyright@cpanel.net                                         http://cpanel.net
# This code is subject to the cPanel license. Unauthorized copying is prohibited

use strict;
use warnings;

use Test::More tests => 4;
use Test::Trap;
use File::Temp;

use FindBin;

use Cpanel::FileUtils::Copy ();

use lib "/usr/local/cpanel/t/lib";
use Temp::User::Cpanel ();

BEGIN { @INC = grep !/^\Q$FindBin::Bin\E/, @INC };    # undo what Temp::User::Cpanel does to @INC so creating a user doesn’t barf with errors about things it can't access

require_ok("$FindBin::Bin/../SOURCES/cpanel-scripts-ea-tomcat85") or die "Could not load scripts::ea_tomcat85 modulino for testing\n";

my @subcmds = qw(status add rem);

# FWiW: this test may seem odd:
#     is( $trap->exit, undef, "… exits clean" );
# if run() was executed via script it would have exited 0 but
# the tests we call the function directly so no exit() was invoked

subtest "help/hint [subcmd]" => sub {
    plan tests => 40;

    # Commands

    trap { scripts::ea_tomcat85::run() };
    like( $trap->stdout, qr/Missing command/, "not args gives reason" );
    unlike( $trap->stdout, qr/given domain/, "no args does hint" );
    is( $trap->exit, undef, "no args exits clean" );

    trap { scripts::ea_tomcat85::run("help") };
    unlike( $trap->stdout, qr/Missing command/, "help arg does not give reason" );
    like( $trap->stdout, qr/given domain/, "help arg does help" );
    is( $trap->exit, undef, "help arg exits clean" );

    trap { scripts::ea_tomcat85::run("hint") };
    unlike( $trap->stdout, qr/Missing command/, "hint arg does not give reason" );
    unlike( $trap->stdout, qr/given domain/,    "hint arg does hint" );
    is( $trap->exit, undef, "hint arg exits clean" );

    trap { scripts::ea_tomcat85::run("derp") };
    like( $trap->stdout, qr/Unrecognized command 'derp'/, "unknown command gives reason" );
    unlike( $trap->stdout, qr/given domain/, "unknown arg does hint" );
    is( $trap->exit, undef, "unknown arg exits clean" );    # seem hinky, but its fhow App::CmdDispatch works ¯\_(ツ)_/¯

    for my $subcmd (@subcmds) {
        my $pipe_delim = join( "|", grep { $_ ne $subcmd } @subcmds );

        trap { scripts::ea_tomcat85::run( "help", $subcmd ) };
        like( $trap->stdout, qr/$subcmd <domain>/, "`help $subcmd` does contains $subcmd" );
        like( $trap->stdout, qr/given domain/,     "`help $subcmd` does help" );
        unlike( $trap->stdout, qr/(?:$pipe_delim)/, "`help $subcmd` does not contain other commands" );
        is( $trap->exit, undef, "`help $subcmd` exits clean" );

        trap { scripts::ea_tomcat85::run( "hint", $subcmd ) };
        like( $trap->stdout, qr/$subcmd <domain>/, "`hint $subcmd` does contains $subcmd" );
        unlike( $trap->stdout, qr/given domain/,    "`hint $subcmd` does hint" );
        unlike( $trap->stdout, qr/(?:$pipe_delim)/, "`hint $subcmd` does not contain other commands" );
        is( $trap->exit, undef, "`hint $subcmd` exits clean" );
    }

    # alias
    trap { scripts::ea_tomcat85::run( "help", "remove" ) };
    like( $trap->stdout, qr/remove\s+:\s+rem/, "`help remove` shows remove as an alias of rem" );
    is( $trap->exit, undef, "`help remove` alias exits clean" );

    trap { scripts::ea_tomcat85::run( "hint", "remove" ) };
    like( $trap->stdout, qr/remove\s+:\s+rem/, "`hint remove` shows remove as an alias of rem" );
    is( $trap->exit, undef, "`hint remove` alias exits clean" );
};

subtest "[subcmd] invalid domain" => sub {
    plan tests => 36;

    for my $subcmd (@subcmds) {
        trap { scripts::ea_tomcat85::run($subcmd) };
        like( $trap->stderr, qr/Domain argument is missing/, "`$subcmd` w/out domain gives warning" );
        like( $trap->stdout, qr/given domain/, "`$subcmd` w/out domain does help" );
        is( $trap->exit, 1, "`$subcmd` w/out domain exits unclean" );

        trap { scripts::ea_tomcat85::run( $subcmd, "i-do-not-exist-$$.com" ) };
        like( $trap->stderr, qr/Domain argument is invalid/, "`$subcmd <non-existent domain>` gives warning" );
        like( $trap->stdout, qr/given domain/, "`$subcmd <non-existent domain>` does help" );
        is( $trap->exit, 1, "`$subcmd <non-existent domain>` exits unclean" );

        trap { scripts::ea_tomcat85::run( $subcmd, "i’m not even a domain" ) };
        like( $trap->stderr, qr/Domain argument is invalid/, "`$subcmd <non-FQDN>` gives warning" );
        like( $trap->stdout, qr/given domain/, "`$subcmd <non-FQDN>` does help" );
        is( $trap->exit, 1, "`$subcmd <non-FQDN>` exits unclean" );

        # this should never happen but juuuust in case
        {
            my $user = "derpy";
            no warnings "redefine";
            local *Cpanel::AcctUtils::DomainOwner::Tiny::getdomainowner = sub { return $user };
            local *Cpanel::Config::LoadUserDomains::loaduserdomains = sub { return { $user => [] } };

            trap { scripts::ea_tomcat85::run( $subcmd, "i-somehow-belong-to-user-but-am-not-in-its-list-of-domains-$$.com" ) };
            like( $trap->stderr, qr/The domain does not exist in user’s domain/, "`$subcmd <weird state domain>` gives warning" );
            like( $trap->stdout, qr/given domain/, "`$subcmd <weird state  domain>` does help" );
            is( $trap->exit, 1, "`$subcmd <weird state  domain>` exits unclean" );
        }
    }
};

subtest "[subcmd] valid domain - happy path" => sub {
    plan tests => 1;
    ok("WiP");

    my $dir = File::Temp->newdir();

    # since server.xml and this script are installed by the same RPM this should be good
    Cpanel::FileUtils::Copy::safecopy( $scripts::ea_tomcat85::serverxml_path, "$dir/server.xml" )
      or BAIL_OUT("Could not setup server.xml ($scripts::ea_tomcat85::serverxml_path missing?)\n");    # safecopy() already spews warnings and errors
    no warnings 'once';
    local $scripts::ea_tomcat85::serverxml_path = "$dir/server.xml";
    use warnings 'once';

    no warnings "redefine";
    local *scripts::ea_tomcat85::_finalize                = sub { };
    local *Cpanel::ConfigFiles::Apache::dir_conf_userdata = sub { $dir };
    use warnings "redefine";

    my $user = Temp::User::Cpanel->new();
    diag( explain($user) );

    # status actual.domain == disabled
    # add actual.domain == adds to domain
    # status actual.domain == enabled
    # add actual.domain == does help w/ message
    # rem actual.domain == removes from domain
    # status actual.domain == disabled
    # rem actual.domain == does help w/ message
    # remove works the same as rem
};
