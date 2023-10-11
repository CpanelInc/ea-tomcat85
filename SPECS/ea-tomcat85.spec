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
Version: 8.5.94
# Doing release_prefix this way for Release allows for OBS-proof versioning, See EA-4572 for more details
%define release_prefix 2
Release: %{release_prefix}%{?dist}.cpanel
License: Apache License, 2.0
Group:   System Environment/Daemons
URL: http://tomcat.apache.org/
Source0: https://www-us.apache.org/dist/tomcat/tomcat-8/v%{version}/bin/apache-tomcat-%{version}.tar.gz
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

if [ -x "/usr/local/cpanel/scripts/ea-tomcat85" ]; then
    /usr/local/cpanel/scripts/ea-tomcat85 all stop
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
/usr/local/cpanel/scripts/ea-tomcat85 all stop

%posttrans
if [ -x "/usr/local/cpanel/scripts/ea-tomcat85" ]; then
    /usr/local/cpanel/scripts/ea-tomcat85 all restart
fi

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

%post

# This is will ensure that "Tomcat Manager" appears in the left menu in the UI
/usr/local/cpanel/scripts/rebuild_whm_chrome

%postun

# This is will ensure that "Tomcat Manager" no longer appears in the left menu in the UI
/usr/local/cpanel/scripts/rebuild_whm_chrome

%changelog
* Tue Oct 10 2023 Cory McIntire <cory@cpanel.net> - 8.5.94-1
- EA-11728: Update ea-tomcat85 from v8.5.93 to v8.5.94
- Request smuggling CVE-2023-45648
- Denial of Service CVE-2023-44487
- Information Disclosure CVE-2023-42795
- Denial of Service CVE-2023-42794

* Fri Oct 06 2023 Travis Holloway <t.holloway@cpanel.net> - 8.5.93-2
- EA-11593: Update dead faster start up link

* Mon Aug 28 2023 Cory McIntire <cory@cpanel.net> - 8.5.93-1
- EA-11635: Update ea-tomcat85 from v8.5.92 to v8.5.93
- Open redirect CVE-2023-41080

* Mon Aug 14 2023 Cory McIntire <cory@cpanel.net> - 8.5.92-1
- EA-11607: Update ea-tomcat85 from v8.5.91 to v8.5.92

* Thu Jul 13 2023 Cory McIntire <cory@cpanel.net> - 8.5.91-1
- EA-11550: Update ea-tomcat85 from v8.5.90 to v8.5.91

* Thu Jun 15 2023 Cory McIntire <cory@cpanel.net> - 8.5.90-1
- EA-11498: Update ea-tomcat85 from v8.5.89 to v8.5.90

* Thu Jun 15 2023 Dan Muey <dan@cpanel.net> - 8.5.89-2
- ZC-11016: Add back erroneously removed `DISABLE_BUILD` to Makefile

* Mon May 22 2023 Cory McIntire <cory@cpanel.net> - 8.5.89-1
- EA-11428: Update ea-tomcat85 from v8.5.88 to v8.5.89
- Information disclosure CVE-2023-34981

* Tue May 09 2023 Brian Mendoza <brian.mendoza@cpanel.net> - 8.5.88-2
- ZC-10936: Clean up Makefile and remove debug-package-nil

* Thu Apr 20 2023 Cory McIntire <cory@cpanel.net> - 8.5.88-1
- EA-11369: Update ea-tomcat85 from v8.5.87 to v8.5.88
- Apache Tomcat denial of service CVE-2023-28709

* Mon Mar 06 2023 Cory McIntire <cory@cpanel.net> - 8.5.87-1
- EA-11283: Update ea-tomcat85 from v8.5.86 to v8.5.87

* Mon Feb 27 2023 Cory McIntire <cory@cpanel.net> - 8.5.86-1
- EA-11270: Update ea-tomcat85 from v8.5.85 to v8.5.86
- Apache Tomcat information disclosure CVE-2023-28708

* Fri Jan 20 2023 Cory McIntire <cory@cpanel.net> - 8.5.85-1
- EA-11177: Update ea-tomcat85 from v8.5.84 to v8.5.85
- Apache Tomcat denial of service CVE-2023-24998

* Thu Nov 24 2022 Cory McIntire <cory@cpanel.net> - 8.5.84-1
- EA-11072: Update ea-tomcat85 from v8.5.83 to v8.5.84
- Apache Tomcat JsonErrorReportValve injection CVE-2022-45143

* Tue Oct 11 2022 Cory McIntire <cory@cpanel.net> - 8.5.83-1
- EA-10980: Update ea-tomcat85 from v8.5.82 to v8.5.83
- Apache Tomcat request smuggling CVE-2022-42252

* Mon Aug 15 2022 Cory McIntire <cory@cpanel.net> - 8.5.82-1
- EA-10878: Update ea-tomcat85 from v8.5.81 to v8.5.82
- Apache Tomcat XSS in examples web application CVE-2022-34305

* Mon Jun 13 2022 Cory McIntire <cory@cpanel.net> - 8.5.81-1
- EA-10761: Update ea-tomcat85 from v8.5.79 to v8.5.81

* Tue May 24 2022 Cory McIntire <cory@cpanel.net> - 8.5.79-1
- EA-10726: Update ea-tomcat85 from v8.5.78 to v8.5.79

* Thu Apr 07 2022 Dan Muey <dan@cpanel.net> - 8.5.78-2
- ZC-9892: Set `unpackWARs` to false initially

* Fri Apr 01 2022 Cory McIntire <cory@cpanel.net> - 8.5.78-1
- EA-10604: Update ea-tomcat85 from v8.5.77 to v8.5.78

* Fri Mar 18 2022 Cory McIntire <cory@cpanel.net> - 8.5.77-1
- EA-10578: Update ea-tomcat85 from v8.5.76 to v8.5.77

* Tue Mar 01 2022 Cory McIntire <cory@cpanel.net> - 8.5.76-1
- EA-10523: Update ea-tomcat85 from v8.5.75 to v8.5.76

* Thu Jan 20 2022 Cory McIntire <cory@cpanel.net> - 8.5.75-1
- EA-10449: Update ea-tomcat85 from v8.5.73 to v8.5.75

* Thu Nov 18 2021 Cory McIntire <cory@cpanel.net> - 8.5.73-1
- EA-10280: Update ea-tomcat85 from v8.5.72 to v8.5.73

* Mon Oct 11 2021 Cory McIntire <cory@cpanel.net> - 8.5.72-1
- EA-10188: Update ea-tomcat85 from v8.5.71 to v8.5.72

* Thu Sep 16 2021 Cory McIntire <cory@cpanel.net> - 8.5.71-1
- EA-10109: Update ea-tomcat85 from v8.5.70 to v8.5.71

* Thu Aug 19 2021 Cory McIntire <cory@cpanel.net> - 8.5.70-1
- EA-10058: Update ea-tomcat85 from v8.5.69 to v8.5.70

* Fri Jul 09 2021 Cory McIntire <cory@cpanel.net> - 8.5.69-1
- EA-9950: Update ea-tomcat85 from v8.5.68 to v8.5.69

* Thu Jun 17 2021 Cory McIntire <cory@cpanel.net> - 8.5.68-1
- EA-9876: Update ea-tomcat85 from v8.5.66 to v8.5.68

* Thu May 13 2021 Cory McIntire <cory@cpanel.net> - 8.5.66-1
- EA-9772: Update ea-tomcat85 from v8.5.65 to v8.5.66

* Fri Apr 23 2021 Travis Holloway <t.holloway@cpanel.net> - 8.5.65-1
- EA-9717: Update ea-tomcat85 from v8.5.64 to v8.5.65

* Tue Apr 06 2021 Cory McIntire <cory@cpanel.net> - 8.5.64-1
- EA-9676: Update ea-tomcat85 from v8.5.63 to v8.5.64

* Thu Feb 04 2021 Cory McIntire <cory@cpanel.net> - 8.5.63-1
- EA-9566: Update ea-tomcat85 from v8.5.61 to v8.5.63

* Mon Jan 04 2021 Cory McIntire <cory@cpanel.net> - 8.5.61-1
- EA-9505: Update ea-tomcat85 from v8.5.60 to v8.5.61

* Sun Nov 29 2020 Cory McIntire <cory@cpanel.net> - 8.5.60-1
- EA-9449: Update ea-tomcat85 from v8.5.59 to v8.5.60

* Mon Oct 12 2020 Cory McIntire <cory@cpanel.net> - 8.5.59-1
- EA-9358: Update ea-tomcat85 from v8.5.58 to v8.5.59

* Fri Sep 18 2020 Cory McIntire <cory@cpanel.net> - 8.5.58-1
- EA-9308: Update ea-tomcat85 from v8.5.57 to v8.5.58

* Thu Jul 09 2020 Cory McIntire <cory@cpanel.net> - 8.5.57-1
- EA-9151: Update ea-tomcat85 from v8.5.56 to v8.5.57

* Mon Jun 29 2020 Julian Brown <julian.brown@cpanel.net> - 8.5.56-2
- ZC-6869: Fix for C8

* Fri Jun 12 2020 Cory McIntire <cory@cpanel.net> - 8.5.56-1
- EA-9110: Update ea-tomcat85 from v8.5.55 to v8.5.56

* Thu May 14 2020 Cory McIntire <cory@cpanel.net> - 8.5.55-1
- EA-9060: Update ea-tomcat85 from v8.5.54 to v8.5.55

* Thu Apr 16 2020 Cory McIntire <cory@cpanel.net> - 8.5.54-1
- EA-9008: Update ea-tomcat85 from v8.5.53 to v8.5.54

* Mon Mar 30 2020 Cory McIntire <cory@cpanel.net> - 8.5.53-1
- EA-8948: Update ea-tomcat85 from v8.5.51 to v8.5.53

* Thu Feb 27 2020 Tim Mullin <tim@cpanel.net> - 8.5.51-2
- EA-8885: Updated our setup script to handle changes to the 8.5.51 server.xml file
- EA-8886: Set secretRequired to false for the AJP connector

* Fri Feb 21 2020 Cory McIntire <cory@cpanel.net> - 8.5.51-1
- EA-8875: Update ea-tomcat85 from v8.5.50 to v8.5.51

* Wed Jan 22 2020 Cory McIntire <cory@cpanel.net> - 8.5.50-1
- EA-8842: Update ea-tomcat85 from v8.5.49 to v8.5.50

* Wed Dec 04 2019 Cory McIntire <cory@cpanel.net> - 8.5.49-1
- EA-8780: Update ea-tomcat85 from v8.5.47 to v8.5.49

* Tue Oct 15 2019 Cory McIntire <cory@cpanel.net> - 8.5.47-1
- EA-8702: Update ea-tomcat85 from v8.5.46 to v8.5.47

* Fri Sep 27 2019 Cory McIntire <cory@cpanel.net> - 8.5.46-1
- EA-8671: Update ea-tomcat85 from v8.5.45 to v8.5.46

* Mon Sep 09 2019 Tim Mullin <tim@cpanel.net> - 8.5.45-2
- EA-8645: Update spec file to use %{version} in source file

* Tue Sep 03 2019 Cory McIntire <cory@cpanel.net> - 8.5.45-1
- EA-8637: Update ea-tomcat85 from v8.5.43 to v8.5.45

* Thu Aug 15 2019 Cory McIntire <cory@cpanel.net> - 8.5.43-1
- EA-8619: Update ea-tomcat85 from v8.5.40 to v8.5.43

* Wed Jul 31 2019 Tim Mullin <tim@cpanel.net> - 8.5.40-2
- EA-8590: Fix syntax errors in user-init.sh

* Wed May 08 2019 Tim Mullin <tim@cpanel.net> - 8.5.40-1
- EA-8240: Update to 8.5.40

* Fri Mar 22 2019 Tim Mullin <tim@cpanel.net> - 8.5.37-2
- EA-8241: Make README symlink errors non-fatal

* Wed Jan 30 2019 Tim Mullin <tim@cpanel.net> - 8.5.37-1
- EA-8186: Update to 8.5.37

* Mon Nov 19 2018 Daniel Muey <dan@cpanel.net> - 8.5.32-16
- ZC-4478: Show error from port authority for clarity

* Wed Nov 14 2018 Daniel Muey <dan@cpanel.net> - 8.5.32-15
- ZC-4462: work around chdir-for-security w/ dropped privs issue

* Thu Nov 08 2018 Tim Mullin <tim@cpanel.net> - 8.5.32-14
- EA-7998: Ensure "Tomcat Manager" appears and is searchable in left menu

* Tue Oct 30 2018 Daniel Muey <dan@cpanel.net> - 8.5.32-13
- ZC-4427: Fix cosmetic USER issue caused by Cpanel::AccessIds lack of setting ENV
- Fix stop/restart scriptlet ordering

* Mon Oct 22 2018 Cory McIntire <cory@cpanel.net> - 8.5.32-12
- EA-7824: Move from EA4-experimental into EA4 production.

* Tue Oct 16 2018 Daniel Muey <dan@cpanel.net> - 8.5.32-11
- ZC-4291: Preserve user’s apps on removal

* Thu Oct 04 2018 Daniel Muey <dan@cpanel.net> - 8.5.32-10
- ZC-4319: Minor security improvements
- ZC-4318: do not suppress errors from code run under dropped privileges
- ZC-4303: do not load external DTDs or external entities in tomcat’s XML files
- ZC-4299: set umask when doing things as the user for better permissions
- ZC-4300: remove pointless redirectPort that is in the default setup

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
