%global ns_dir /opt/cpanel

# OBS builds the 32-bit targets as arch 'i586', and more typical
# 32-bit architecture is 'i386', but 32-bit archive is named 'x86'.
# 64-bit archive is 'x86-64', rather than 'x86_64'.
%if "%{_arch}" == "i586" || "%{_arch}" == "i386"
%global archive_arch x86
%else
%if "%{_arch}" == "x86_64"
%global archive_arch x86-64
%else
%global archive_arch %{_arch}
%endif
%endif

%if 0%{?centos} >= 7 || 0%{?fedora} >= 17 || 0%{?rhel} >= 7
%global with_systemd 1
%else
%global with_systemd 0
%endif

Name:    ea-tomcat85
Vendor:  cPanel, Inc.
Summary: Tomcat 8.5
Version: 8.5.32
# Doing release_prefix this way for Release allows for OBS-proof versioning, See EA-4572 for more details
%define release_prefix 7
Release: %{release_prefix}%{?dist}.cpanel
License: Apache License, 2.0
Group:   System Environment/Daemons
URL: http://tomcat.apache.org/
Source0: http://mirror.olnevhost.net/pub/apache/tomcat/tomcat-8/v8.5.32/bin/apache-tomcat-8.5.32.tar.gz
Source1: setenv.sh
Source2: ea-tomcat85.logrotate
Source3: ea-tomcat85.service
Source4: chkconfig
Source5: cpanel-scripts-ea-tomcat85
Source6: Ea_tomcat85.pm
Source7: README.FASTERSTARTUP
Source8: README.SECURITY
Source9: README.USER-SERVICE-MANAGEMENT
Source10: user-init.sh
Source11: user-setenv.sh
Source12: user-shutdown.sh
Source13: user-startup.sh
Source14: README.APACHE-PROXY
Source15: README.USER-INSTANCE
Source16: test.jsp

# if I do not have autoreq=0, rpm build will recognize that the ea_
# scripts need perl and some Cpanel pm's to be on the disk.
# unfortunately they cannot be satisfied via the requires: tags.
Autoreq: 0

Requires: java-1.8.0-openjdk java-1.8.0-openjdk-devel
Requires: jakarta-commons-daemon jakarta-commons-daemon-jsvc
Requires: mysql-connector-java
Requires: ea-apache24-mod_proxy_ajp

# Create Tomcat user/group as we definitely do not want this running as root.
Requires(pre): /usr/sbin/useradd, /usr/bin/getent
Requires(postun): /usr/sbin/userdel

%if %{with_systemd}
BuildRequires: systemd-units
BuildRequires: systemd
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd
# For triggerun
Requires(post): systemd-sysv
%else
BuildRequires: chkconfig
Requires: initscripts
Requires(post): /sbin/chkconfig
Requires(preun): /sbin/chkconfig, /sbin/service
Requires(postun): /sbin/service
%endif
Requires(pre):  shadow-utils

%description
Tomcat is the servlet container that is used in the official Reference
Implementation for the Java Servlet and JavaServer Pages technologies.
The Java Servlet and JavaServer Pages specifications are developed by
Sun under the Java Community Process.

Tomcat is developed in an open and participatory environment and
released under the Apache Software License version 2.0. Tomcat is intended
to be a collaboration of the best-of-breed developers from around the world.

%prep
%setup -qn apache-tomcat-%{version}

%pre

# add the group if we need it:
if [ $(/usr/bin/getent group tomcat | wc -c) -eq 0 ];
    then /usr/sbin/groupadd -r tomcat;
fi

# if the user already exists, just add to group
if [ $(/usr/bin/getent passwd tomcat | wc -c) -ne 0 ];
    then usermod -g tomcat tomcat;
else
# otherwise lets just create the user like normal
    /usr/sbin/useradd -r -d /opt/cpanel/%{name} -s /sbin/nologin -g tomcat tomcat
fi

%build
# empty build section

%install
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf %{buildroot}
mkdir -p $RPM_BUILD_ROOT/opt/cpanel/ea-tomcat85
cp -r ./* $RPM_BUILD_ROOT/opt/cpanel/ea-tomcat85
cp %{SOURCE1} $RPM_BUILD_ROOT/opt/cpanel/ea-tomcat85/bin/

# put logs under /var/log ...
mkdir -p $RPM_BUILD_ROOT/var/log/ea-tomcat85
rmdir $RPM_BUILD_ROOT/opt/cpanel/ea-tomcat85/logs
ln -sf /var/log/ea-tomcat85 $RPM_BUILD_ROOT/opt/cpanel/ea-tomcat85/logs

# ... and rotate them:
mkdir -p $RPM_BUILD_ROOT/etc/logrotate.d
cp %{SOURCE2} $RPM_BUILD_ROOT/etc/logrotate.d/ea-tomcat85

ln -sf /var/run $RPM_BUILD_ROOT/opt/cpanel/ea-tomcat85/run

%if %{with_systemd}
mkdir -p $RPM_BUILD_ROOT%{_unitdir}
cp %{SOURCE3} $RPM_BUILD_ROOT%{_unitdir}/ea_tomcat85.service
%else
mkdir -p $RPM_BUILD_ROOT%{_initddir}
cp %{SOURCE4} $RPM_BUILD_ROOT%{_initddir}/ea_tomcat85
%endif

mkdir -p $RPM_BUILD_ROOT/var/run/ea-tomcat85

mkdir -p $RPM_BUILD_ROOT/usr/local/cpanel/scripts
cp %{SOURCE5} $RPM_BUILD_ROOT/usr/local/cpanel/scripts/ea-tomcat85
ln -s restartsrv_base $RPM_BUILD_ROOT/usr/local/cpanel/scripts/restartsrv_ea_tomcat85

mkdir -p $RPM_BUILD_ROOT/usr/local/cpanel/Cpanel/ServiceManager/Services
cp %{SOURCE6} $RPM_BUILD_ROOT/usr/local/cpanel/Cpanel/ServiceManager/Services/Ea_tomcat85.pm

# private instance items
cp %{SOURCE7} $RPM_BUILD_ROOT/opt/cpanel/ea-tomcat85/README.FASTERSTARTUP
cp %{SOURCE8} $RPM_BUILD_ROOT/opt/cpanel/ea-tomcat85/README.SECURITY
cp %{SOURCE9} $RPM_BUILD_ROOT/opt/cpanel/ea-tomcat85/README.USER-SERVICE-MANAGEMENT
cp %{SOURCE14} $RPM_BUILD_ROOT/opt/cpanel/ea-tomcat85/README.APACHE-PROXY
cp %{SOURCE15} $RPM_BUILD_ROOT/opt/cpanel/ea-tomcat85/README.USER-INSTANCE
cp %{SOURCE16} $RPM_BUILD_ROOT/opt/cpanel/ea-tomcat85/test.jsp

cp %{SOURCE10} $RPM_BUILD_ROOT/opt/cpanel/ea-tomcat85/bin/user-init.sh
cp %{SOURCE11} $RPM_BUILD_ROOT/opt/cpanel/ea-tomcat85/bin/user-setenv.sh
cp %{SOURCE12} $RPM_BUILD_ROOT/opt/cpanel/ea-tomcat85/bin/user-shutdown.sh
cp %{SOURCE13} $RPM_BUILD_ROOT/opt/cpanel/ea-tomcat85/bin/user-startup.sh

mkdir -p $RPM_BUILD_ROOT/opt/cpanel/ea-tomcat85/user-conf
cp -r ./conf/* $RPM_BUILD_ROOT/opt/cpanel/ea-tomcat85/user-conf

%clean
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf %{buildroot}

%post

/usr/local/cpanel/scripts/restartsrv_ea_tomcat85
/usr/local/cpanel/whostmgr/docroot/themes/x/rebuildtmpl

%preun

/usr/local/cpanel/scripts/restartsrv_ea_tomcat85 stop

# We don't want to remove the user if the customer had the user already
# Might have data they want including mail spool
# We DO NOT set up mail for OUR user, so no need for -r in userdel command
# if it is our user.

if [ `getent passwd tomcat | cut -d: -f6` == "/opt/cpanel/ea-tomcat85" ];
    then /usr/sbin/userdel tomcat
fi

# userdel should remove the group but let us make sure
# if at some point later it does not we might need something close to the below
# current this exits with status 2 and causes a warning so taking out
# /usr/bin/getent group tomcat && /usr/sbin/groupdel tomcat

%postun

/usr/local/cpanel/whostmgr/docroot/themes/x/rebuildtmpl

%files
%attr(0755,root,root) /usr/local/cpanel/scripts/ea-tomcat85
/usr/local/cpanel/scripts/restartsrv_ea_tomcat85
/usr/local/cpanel/Cpanel/ServiceManager/Services/Ea_tomcat85.pm
%defattr(-,tomcat,tomcat,-)
/opt/cpanel/ea-tomcat85
%attr(0755,root,root) /opt/cpanel/ea-tomcat85/user-conf
%attr(0644,root,root) /opt/cpanel/ea-tomcat85/README*
%attr(0755,root,root) /opt/cpanel/ea-tomcat85/bin/user-*.sh
%config(noreplace) %attr(0755,tomcat,tomcat) /opt/cpanel/ea-tomcat85/bin/setenv.sh
%config(noreplace) %attr(0640,tomcat,tomcat) /opt/cpanel/ea-tomcat85/conf/server.xml
%config(noreplace) %attr(0640,tomcat,tomcat) /opt/cpanel/ea-tomcat85/conf/context.xml
%config(noreplace) %attr(0640,tomcat,tomcat) /opt/cpanel/ea-tomcat85/conf/jaspic-providers.xml
%config(noreplace) %attr(0640,tomcat,tomcat) /opt/cpanel/ea-tomcat85/conf/jaspic-providers.xsd
%config(noreplace) %attr(0640,tomcat,tomcat) /opt/cpanel/ea-tomcat85/conf/tomcat-users.xml
%config(noreplace) %attr(0640,tomcat,tomcat) /opt/cpanel/ea-tomcat85/conf/tomcat-users.xsd
%config(noreplace) %attr(0640,tomcat,tomcat) /opt/cpanel/ea-tomcat85/conf/web.xml
%config(noreplace) %attr(0640,tomcat,tomcat) /opt/cpanel/ea-tomcat85/conf/catalina.policy
%config(noreplace) %attr(0640,tomcat,tomcat) /opt/cpanel/ea-tomcat85/conf/catalina.properties
%config(noreplace) %attr(0640,tomcat,tomcat) /opt/cpanel/ea-tomcat85/conf/logging.properties
%config(noreplace) %attr(0640,tomcat,tomcat) /opt/cpanel/ea-tomcat85/webapps/ROOT/WEB-INF/web.xml
%config(noreplace) %attr(0640,tomcat,tomcat) /opt/cpanel/ea-tomcat85/webapps/manager/META-INF/context.xml
%config(noreplace) %attr(0640,tomcat,tomcat) /opt/cpanel/ea-tomcat85/webapps/manager/WEB-INF/web.xml
%config(noreplace) %attr(0640,tomcat,tomcat) /opt/cpanel/ea-tomcat85/webapps/host-manager/META-INF/context.xml
%config(noreplace) %attr(0640,tomcat,tomcat) /opt/cpanel/ea-tomcat85/webapps/host-manager/WEB-INF/web.xml

%dir /var/log/ea-tomcat85
%dir %attr(0770,root,tomcat) /var/run/ea-tomcat85
%ghost %attr(0640,tomcat,tomcat) /var/run/ea-tomcat85/catalina.pid
/etc/logrotate.d/ea-tomcat85
%if %{with_systemd}
# Must be root root here for write permissions
%config(noreplace) %attr(0644,root,root) %{_unitdir}/ea_tomcat85.service
%else
%attr(0755,tomcat,tomcat) %{_initddir}/ea_tomcat85
%endif

%changelog
* Tue Sep 04 2018 Daniel Muey <dan@cpanel.net> - 8.5.32-7
- ZC-4211: improve tomcat user detection

* Thu Aug 23 2018 Daniel Muey <dan@cpanel.net> - 8.5.32-6
- ZC-4037: switch tomcat to private-instance approach

* Thu Aug 02 2018 Daniel Muey <dan@cpanel.net> - 8.5.32-5
- ZC-4088: remove tomcat from nobody group

* Thu Jul 26 2018 Daniel Muey <dan@cpanel.net> - 8.5.32-4
- ZC-4026: Run tomcat as the user tomcat

* Thu Jul 26 2018 Cory McIntire <cory@cpanel.net> - 8.5.32-3
- EA-7750: ea-tomcat85 should leave all conf files in place on upgrade

* Tue Jul 24 2018 Daniel Muey <dan@cpanel.net> - 8.5.32-2
- ZC-4024: encode values in node in case the code in question is ever used elsewhere

* Tue Jul 24 2018 Cory McIntire <cory@cpanel.net> - 8.5.32-1
- EA-7691: Update to 8.5.32 to handle CVEs
  CVE-2018-1304 Security constraints mapped to context root are ignored
  CVE-2018-1305 Security constraint annotations applied too late
  CVE-2018-1336 A bug in the UTF-8 decoder can lead to DoS
  CVE-2018-8014 CORS filter has insecure defaults
  CVE-2018-8034 host name verification missing in WebSocket client
  CVE-2018-8037 Due to a mishandling of close in NIO/NIO2 connectors user sessions can get mixed up

* Wed Jun 20 2018 Daniel Muey <dan@cpanel.net> - 8.5.24-8
- ZC-3871: Rebuild WHM menu caches so the EA4 tomcat icon will show/hide correctly

* Tue Jun 19 2018 Daniel Muey <dan@cpanel.net> - 8.5.24-7
- EA-7489: General UX Improvements
    RPM:

    - add Requires for mysql-connector-java
    - add Requires for jakarta-commons-daemon and jakarta-commons-daemon-jsvc

    cpanel script:

    - Have its Include match `/servlets?/` in subdirectories
    - Add `refresh` subcommand
    - Add --verbose support to `status` sub command
    - Add support for custom server.xml `<Host>` entry
    - Add support for custom httpd Include
    - cleanup domain’s `work/` and `conf/` files

* Wed May 30 2018 Daniel Muey <dan@cpanel.net> - 8.5.24-6
- EA-7495: Add ULC restartsrv_ea_tomcat85 script

* Thu May 24 2018 Daniel Muey <dan@cpanel.net> - 8.5.24-5
- EA-7514: Add support for skipping reconf/recbuild to cpanel script

* Fri May 11 2018 Daniel Muey <dan@cpanel.net> - 8.5.24-4
- EA-7402: Create initial add/remove tomcat to a domain script

* Tue Apr 17 2018 Daniel Muey <dan@cpanel.net> - 8.5.24-3
- ZC-3464: Add ea-apache24-mod_proxy_ajp as a requirement so we have a connector available

* Wed Mar 14 2018 Cory McIntire <cory@cpanel.net> - 8.5.24-2
- EA-7297: Fix rpmlint errors and warnings
- Credit: https://github.com/dkasyanov

* Thu Jan 18 2018 Dan Muey <dan@cpanel.net> - 8.5.24-1
- ZC-3244: Initial ea-tomcat85 (v8.5.24)
