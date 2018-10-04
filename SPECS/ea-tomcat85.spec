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
%define release_prefix 10
Release: %{release_prefix}%{?dist}.cpanel
License: Apache License, 2.0
Group:   System Environment/Daemons
URL: http://tomcat.apache.org/
Source0: http://mirror.olnevhost.net/pub/apache/tomcat/tomcat-8/v8.5.32/bin/apache-tomcat-8.5.32.tar.gz
Source1: setenv.sh
Source2: sample.ea-tomcat85.logrotate
Source3: sample.ea-tomcat85.service
Source4: sample.ea-tomcat85.initd
Source5: cpanel-scripts-ea-tomcat85
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
Source17: README.SHARED-SERVICE-MANAGEMENT

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
cp %{SOURCE2} $RPM_BUILD_ROOT/opt/cpanel/ea-tomcat85/
cp %{SOURCE3} $RPM_BUILD_ROOT/opt/cpanel/ea-tomcat85/
cp %{SOURCE4} $RPM_BUILD_ROOT/opt/cpanel/ea-tomcat85/
cp /etc/rc.d/init.d/functions $RPM_BUILD_ROOT/opt/cpanel/ea-tomcat85/bin/user-functions

# put logs under /var/log ...
mkdir -p $RPM_BUILD_ROOT/var/log/ea-tomcat85
rmdir $RPM_BUILD_ROOT/opt/cpanel/ea-tomcat85/logs
ln -sf /var/log/ea-tomcat85 $RPM_BUILD_ROOT/opt/cpanel/ea-tomcat85/logs

ln -sf /var/run $RPM_BUILD_ROOT/opt/cpanel/ea-tomcat85/run

mkdir -p $RPM_BUILD_ROOT/var/run/ea-tomcat85

mkdir -p $RPM_BUILD_ROOT/usr/local/cpanel/scripts
cp %{SOURCE5} $RPM_BUILD_ROOT/usr/local/cpanel/scripts/ea-tomcat85

# private instance items
cp %{SOURCE7} $RPM_BUILD_ROOT/opt/cpanel/ea-tomcat85/README.FASTERSTARTUP
cp %{SOURCE8} $RPM_BUILD_ROOT/opt/cpanel/ea-tomcat85/README.SECURITY
cp %{SOURCE9} $RPM_BUILD_ROOT/opt/cpanel/ea-tomcat85/README.USER-SERVICE-MANAGEMENT
cp %{SOURCE14} $RPM_BUILD_ROOT/opt/cpanel/ea-tomcat85/README.APACHE-PROXY
cp %{SOURCE15} $RPM_BUILD_ROOT/opt/cpanel/ea-tomcat85/README.USER-INSTANCE
cp %{SOURCE16} $RPM_BUILD_ROOT/opt/cpanel/ea-tomcat85/test.jsp
cp %{SOURCE17} $RPM_BUILD_ROOT/opt/cpanel/ea-tomcat85/README.SHARED-SERVICE-MANAGEMENT

cp %{SOURCE10} $RPM_BUILD_ROOT/opt/cpanel/ea-tomcat85/bin/user-init.sh
cp %{SOURCE11} $RPM_BUILD_ROOT/opt/cpanel/ea-tomcat85/bin/user-setenv.sh
cp %{SOURCE12} $RPM_BUILD_ROOT/opt/cpanel/ea-tomcat85/bin/user-shutdown.sh
cp %{SOURCE13} $RPM_BUILD_ROOT/opt/cpanel/ea-tomcat85/bin/user-startup.sh

mkdir -p $RPM_BUILD_ROOT/opt/cpanel/ea-tomcat85/user-conf
cp -r ./conf/* $RPM_BUILD_ROOT/opt/cpanel/ea-tomcat85/user-conf

%clean
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf %{buildroot}

%preun

# upgrade and uninstall
/usr/local/cpanel/scripts/ea-tomcat85 all stop

%post

# upgrade (and install because ... spec files ... but it'll be a no-op if no one has it yet)
/usr/local/cpanel/scripts/ea-tomcat85 all restart

%files
%attr(0755,root,root) /usr/local/cpanel/scripts/ea-tomcat85
%defattr(-,root,tomcat,-)
/opt/cpanel/ea-tomcat85
%attr(0755,root,root) /opt/cpanel/ea-tomcat85/user-conf
%attr(0644,root,root) /opt/cpanel/ea-tomcat85/README*
%attr(0644,root,root) /opt/cpanel/ea-tomcat85/sample*
%attr(0755,root,root) /opt/cpanel/ea-tomcat85/bin/user-*
%config(noreplace) %attr(0755,root,tomcat) /opt/cpanel/ea-tomcat85/bin/setenv.sh
%config(noreplace) %attr(0640,root,tomcat) /opt/cpanel/ea-tomcat85/conf/server.xml
%config(noreplace) %attr(0640,root,tomcat) /opt/cpanel/ea-tomcat85/conf/context.xml
%config(noreplace) %attr(0640,root,tomcat) /opt/cpanel/ea-tomcat85/conf/jaspic-providers.xml
%config(noreplace) %attr(0640,root,tomcat) /opt/cpanel/ea-tomcat85/conf/jaspic-providers.xsd
%config(noreplace) %attr(0640,root,tomcat) /opt/cpanel/ea-tomcat85/conf/tomcat-users.xml
%config(noreplace) %attr(0640,root,tomcat) /opt/cpanel/ea-tomcat85/conf/tomcat-users.xsd
%config(noreplace) %attr(0640,root,tomcat) /opt/cpanel/ea-tomcat85/conf/web.xml
%config(noreplace) %attr(0640,root,tomcat) /opt/cpanel/ea-tomcat85/conf/catalina.policy
%config(noreplace) %attr(0640,root,tomcat) /opt/cpanel/ea-tomcat85/conf/catalina.properties
%config(noreplace) %attr(0640,root,tomcat) /opt/cpanel/ea-tomcat85/conf/logging.properties
%config(noreplace) %attr(0640,root,tomcat) /opt/cpanel/ea-tomcat85/webapps/ROOT/WEB-INF/web.xml
%config(noreplace) %attr(0640,root,tomcat) /opt/cpanel/ea-tomcat85/webapps/manager/META-INF/context.xml
%config(noreplace) %attr(0640,root,tomcat) /opt/cpanel/ea-tomcat85/webapps/manager/WEB-INF/web.xml
%config(noreplace) %attr(0640,root,tomcat) /opt/cpanel/ea-tomcat85/webapps/host-manager/META-INF/context.xml
%config(noreplace) %attr(0640,root,tomcat) /opt/cpanel/ea-tomcat85/webapps/host-manager/WEB-INF/web.xml

%dir /var/log/ea-tomcat85
%dir %attr(0770,root,tomcat) /var/run/ea-tomcat85
%ghost %attr(0640,tomcat,tomcat) /var/run/ea-tomcat85/catalina.pid

%changelog
* Thu Oct 04 2018 Daniel Muey <dan@cpanel.net> - 8.5.32-10
- ZC-4319: Minor security improvements
- ZC-4318: do not suppress errors from code run under dropped privileges
- ZC-4303: do not load external DTDs or external entities in tomcat’s XML files

* Tue Sep 11 2018 Daniel Muey <dan@cpanel.net> - 8.5.32-9
- ZC-4252: Adjust for private instance in jailshell
- ZC-4198: stop/restart private instances on update/uninstall as appropriate (ZC-4202/ZC-4203)
- ZC-4198: Make private instance default configuration more secure (ZC-4205)

* Tue Sep 04 2018 Daniel Muey <dan@cpanel.net> - 8.5.32-8
- ZC-4142: Change RPM to not run tomcat by default
- ZC-3874: avoid spurious `cat: /var/run/catalina.pid: No such file or directory`
- ZC-4081: do not remove tomcat user
- ZC-4082: change %files so tomcat does not have write access to things it shouldn't

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
