# cpanel - t/SOURCES-cpanel-scripts-ea-tomcat85.t    Copyright 2018 cPanel, Inc.
#                                                           All rights Reserved.
# copyright@cpanel.net                                         http://cpanel.net
# This code is subject to the cPanel license. Unauthorized copying is prohibited

use strict;
use warnings;

use Test::More tests => 6;
use Test::Trap;
use Test::Deep;
use File::Temp;

use FindBin;

use Cpanel::FileUtils::Copy           ();
use Cpanel::AccessIds                 ();
use Cpanel::HTTP::Tiny::FastSSLVerify ();

BEGIN {    # some voo doo necessary since the test isn’t in /usr/local/cpanel/t
    use lib "/usr/local/cpanel/t/lib";
    use Temp::User::Cpanel ();
    @INC = grep !/^\Q$FindBin::Bin\E/, @INC;    # undo what Temp::User::Cpanel does to @INC so creating a user doesn’t barf with errors about things it can't access
}

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

subtest "[subcmd] invalid-arg" => sub {
    plan tests => 43;

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
            like( $trap->stderr, qr/The account “$user” does not own the domain “i-some\S+com”/, "`$subcmd <weird state domain>` gives warning" );
            like( $trap->stdout, qr/given domain/, "`$subcmd <weird state  domain>` does help" );
            is( $trap->exit, 1, "`$subcmd <weird state  domain>` exits unclean" );
        }
    }

    trap { scripts::ea_tomcat85::run( "rem", "localhost" ) };
    like( $trap->stderr, qr/Domain argument is invalid/, "trying to remove localhost gives warning" );
    like( $trap->stdout, qr/given domain/, "trying to remove localhost does help" );
    is( $trap->exit, 1, "trying to remove localhost exits unclean" );

    trap { scripts::ea_tomcat85::run( "list", "derp" ) };
    like( $trap->stderr, qr/“list” does not take any arguments/, "`list <ARG>` gives warning" );
    like( $trap->stdout, qr/given domain/, "`list <ARG>` does help" );
    is( $trap->exit, 1, "`list <ARG>` exits unclean" );

    local $ENV{"scripts::ea_tomcat85::bail_die"} = 1;
    trap { scripts::ea_tomcat85::run( "list", "derp" ) };
    like( $trap->die, qr/“list” does not take any arguments/, "ENV scripts::ea_tomcat85::bail_die make bail out a die instead of exit" );
};

subtest "[subcmd] valid domain - happy path" => sub {
    plan tests => 27;

    my $dir = File::Temp->newdir();

    # since server.xml and this script are installed by the same RPM this should be good
    Cpanel::FileUtils::Copy::safecopy( $scripts::ea_tomcat85::serverxml_dir, $dir )
      or BAIL_OUT("Could not setup server.xml ($scripts::ea_tomcat85::serverxml_dir missing?)\n");    # safecopy() already spews warnings and errors
    no warnings 'once';
    local $scripts::ea_tomcat85::serverxml_dir = $dir;
    local $scripts::ea_tomcat85::work_dir      = "$dir/work";
    mkdir $scripts::ea_tomcat85::work_dir;
    local $scripts::ea_tomcat85::conf_dir = "$dir/conf";
    mkdir $scripts::ea_tomcat85::conf_dir;
    use warnings 'once';

    my $finalized = 0;
    no warnings "redefine";
    local *scripts::ea_tomcat85::_finalize                = sub { $finalized++ };
    local *Cpanel::ConfigFiles::Apache::dir_conf_userdata = sub { $dir };
    use warnings "redefine";

    # some more voo doo necessary since the test isn’t in /usr/local/cpanel/t
    chdir "/" or die "chdir(/) failed: $!\n";
    local $FindBin::Bin = "/";
    my $user   = Temp::User::Cpanel->new();
    my $domain = $user->domain;
    my $uname  = $user->name;

    my %dom_tests = ( main => $domain );    # ¿ TODO/YAGNI: expand to parked, sub, addon, addon’s sub, cpanel proxy ?

    for my $type ( "main", sort grep { $_ ne "main" } keys %dom_tests ) {
        my $dname = $dom_tests{$type};

        mkdir "$scripts::ea_tomcat85::work_dir/$dname";
        mkdir "$scripts::ea_tomcat85::conf_dir/$dname";
        my @tc_doms = _get_list();
        cmp_deeply( \@tc_doms, superbagof("localhost"), "pre $type sanity check: localhost is configured (list)" );

        trap { scripts::ea_tomcat85::run( "status", $dname ) };
        is( $trap->exit, undef, "`status <$type domain>` exits clean when domain is disabled" );
        like( $trap->stdout, qr/^\Q$dname\E: disabled/, "`status <$type domain>` when disabled says its disabled" );

        trap { scripts::ea_tomcat85::run( "add", $dname ) };
        is( $trap->exit, undef, "`add <$type domain>` exits clean" );
        ok( scripts::ea_tomcat85::_domain_has_tomcat85( $uname, $dname ), "`add <$type domain>` adds tomcat85 support" );

        @tc_doms = _get_list();
        cmp_deeply( \@tc_doms, superbagof( "localhost", $dname ), "`add <$type domain>` domain and localhost are listed (list)" );

        trap { scripts::ea_tomcat85::run( "status", $dname ) };
        is( $trap->exit, undef, "`status <$type domain>` exits clean when domain is enabled" );
        like( $trap->stdout, qr/^\Q$dname\E: enabled/, "`status <$type domain>` after enabling says its enabled" );

        trap { scripts::ea_tomcat85::run( "add", $dname ) };
        is( $trap->exit, 1, "`add <$type domain>` exits unclean when domain is already enabled" );
        like( $trap->stderr, qr/The domain already has tomcat 8\.5 support/, "`add <$type domain>` gives warning when domain is already enabled" );
        like( $trap->stdout, qr/given domain/, "`add <$type domain>` does help when domain is already enabled" );

        trap { scripts::ea_tomcat85::run( "rem", $dname ) };
        is( $trap->exit, undef, "`rem <$type domain>` exits clean" );
        ok( !scripts::ea_tomcat85::_domain_has_tomcat85( $uname, $dname ), "`rem <$type domain>` removes tomcat85 support" );
        ok( !-d "$scripts::ea_tomcat85::work_dir/$dname", "`rem <$type domain>` cleans up work dir" );
        ok( !-d "$scripts::ea_tomcat85::conf_dir/$dname", "`rem <$type domain>` cleans up conf dir" );

        @tc_doms = _get_list();
        cmp_deeply( \@tc_doms, superbagof("localhost"), "`rem <$type domain>` does not list domain, localhost is listed (list)" );

        trap { scripts::ea_tomcat85::run( "status", $dname ) };
        is( $trap->exit, undef, "`status <$type domain>` exits clean when domain is disabled" );
        like( $trap->stdout, qr/^\Q$dname\E: disabled/, "`status <$type domain>` after being removed says its disabled" );

        trap { scripts::ea_tomcat85::run( "rem", $dname ) };
        is( $trap->exit, 1, "`rem <$type domain>` exits unclean when domain is already disabled" );
        like( $trap->stderr, qr/The domain does not have tomcat 8\.5 support/, "`rem <$type domain>` gives warning when domain is already disabled" );
        like( $trap->stdout, qr/given domain/, "`rem <$type domain>` does help when domain is already disabled" );

        # smaller subset to verify remove aliases rem correctly (and --no-flush):
        my $cur_finalized = $finalized;
        trap { scripts::ea_tomcat85::run( "add", $dname, "--no-flush" ) };
        like( $trap->stdout, qr/Not rebuilding conf and restarting per --no-flush/, "add <$type domain> --no-flush results in output" );
        is( $finalized, $cur_finalized, "add <$type domain> --no-flush does not call _finalize()" );

        trap { scripts::ea_tomcat85::run( "remove", $dname, "--no-flush" ) };
        like( $trap->stdout, qr/Not rebuilding conf and restarting per --no-flush/, "rem[ove] <$type domain> --no-flush results in output" );
        is( $finalized, $cur_finalized, "rem[ove] <$type domain> --no-flush does not call _finalize()" );

        is( $trap->exit, undef, "`remove <$type domain>` exits clean like rem" );
        ok( !scripts::ea_tomcat85::_domain_has_tomcat85( $uname, $dname ), "`remove <$type domain>` - removes tomcat85 support" );
    }
};

subtest "flush" => sub {
    plan tests => 1;

    my $finalized = 0;
    no warnings "redefine";
    local *scripts::ea_tomcat85::_finalize = sub { $finalized++; };
    trap {
        scripts::ea_tomcat85::run("flush")
    };
    is( $finalized, 1, "flush sub command calls _finalize()" );
};

subtest "test" => sub {
    plan tests => 10;

    my $dir = File::Temp->newdir();
    my $res_hr = { success => 1, content => "oh hai", status => 200 };

    no warnings "redefine", "once";
    local *scripts::ea_tomcat85::_process_args = sub {
        my ( $app, $domain, @args ) = @_;
        my $opts = {};
        $opts->{verbose} = 1 if grep { $_ eq "--verbose" } @args;
        return ( $app, "meuser", $domain, $opts );
    };
    local *Cpanel::AccessIds::do_as_user          = sub { return $dir };
    local *Cpanel::HTTP::Tiny::FastSSLVerify::get = sub { return $res_hr };
    use warnings "redefine", "once";

    # no error: rendered
    trap { scripts::ea_tomcat85::run( "test", "foo.com" ) };
    like( $trap->stdout, qr/foo\.com: ✔︎ \.jsp is processed/, "test <domain> w/ no HTTP error and no JSP tags reports success" );
    is( _dir_cnt($dir), 0, "^^^ cleans up the JSP file" );

    # --verbose
    trap { scripts::ea_tomcat85::run( "test", "foo.com", "--verbose" ) };
    like( $trap->stdout, qr/Testing via this JSP source code:/,  "test <domain> --verbose outputs JSP source - 1" );
    like( $trap->stdout, qr/<%=/m,                               "test <domain> --verbose outputs JSP source - 2" );
    like( $trap->stdout, qr/JSP Response HTML \(200\):\noh hai/, "test <domain> --verbose outputs HTML result" );
    is( _dir_cnt($dir), 0, "^^^ cleans up the JSP file" );

    # no error: not rendered
    $res_hr->{content} = "<%= hi %>";
    trap { scripts::ea_tomcat85::run( "test", "foo.com" ) };
    like( $trap->stdout, qr/foo\.com: ✗ \.jsp is not processed/, "test <domain> w/ no HTTP error and JSP tags reports failure" );
    is( _dir_cnt($dir), 0, "^^^ cleans up the JSP file" );

    # error
    $res_hr->{success} = "";
    trap { scripts::ea_tomcat85::run( "test", "foo.com" ) };
    like( $trap->stdout, qr/foo\.com: HTTP request failed/, "test <domain> w/ HTTP error indicates its failure" );
    is( _dir_cnt($dir), 0, "^^^ cleans up the JSP file" );
};

# TODO: sad path edge case tests (like handling partially enabled domains)

###############
#### helpers ##
###############

sub _dir_cnt {
    my ($dir) = @_;
    opendir my $dh, $dir or die "Could not opendir “$dir”: $!\n";
    my @contents = grep { $_ ne "." && $_ ne ".." } readdir($dh);
    closedir $dh;

    return scalar(@contents);
}

sub _get_list {
    trap { scripts::ea_tomcat85::run("list") };
    return split( "\n", $trap->stdout );
}
