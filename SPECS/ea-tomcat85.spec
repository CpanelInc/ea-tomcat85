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
Version: 8.5.24
# Doing release_prefix this way for Release allows for OBS-proof versioning, See EA-4572 for more details
%define release_prefix 1
Release: %{release_prefix}%{?dist}.cpanel
License: Apache License, 2.0
Group:   System Environment/Daemons
URL: http://tomcat.apache.org/
Source0: http://www-eu.apache.org/dist/tomcat/tomcat-8/v8.5.24/bin/apache-tomcat-8.5.24.tar.gz
Source1: setenv.sh
Source2: ea-tomcat85.logrotate
Source3: tomcat.service
Source4: chkconfig

Requires: java-1.8.0-openjdk java-1.8.0-openjdk-devel

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
%setup -n apache-tomcat-%{version}

%pre
/usr/bin/getent passwd tomcat || /usr/sbin/useradd -r -d /opt/cpanel/%{name} -s /sbin/nologin tomcat
/usr/bin/getent group tomcat || /usr/sbin/groupadd -r tomcat

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

%if %{with_systemd}
mkdir -p $RPM_BUILD_ROOT/usr/lib/systemd/system
cp %{SOURCE3} $RPM_BUILD_ROOT/usr/lib/systemd/system/tomcat.service
%else
mkdir -p $RPM_BUILD_ROOT/etc/init.d
cp %{SOURCE4} $RPM_BUILD_ROOT/etc/init.d/%{name}
%endif

%clean
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf %{buildroot}

%post
%if %{with_systemd}
systemctl daemon-reload
systemctl enable tomcat
systemctl start tomcat
%else
/opt/cpanel/ea-tomcat85/bin/startup.sh
%endif

%postun
%if %{with_systemd}
systemctl stop tomcat
systemctl daemon-reload
%else
/opt/cpanel/ea-tomcat85/bin/shutdown.sh
%endif

/usr/sbin/userdel tomcat
/usr/sbin/groupdel tomcat


%files
%defattr(-,tomcat,nobody,-)
/opt/cpanel/ea-tomcat85
%config(noreplace) %attr(0755,tomcat,nobody) /opt/cpanel/ea-tomcat85/bin/setenv.sh
%dir /var/log/ea-tomcat85
/etc/logrotate.d/ea-tomcat85
%config(noreplace) %attr(0755,tomcat,nobody) /opt/cpanel/ea-tomcat85/bin/setenv.sh
%if %{with_systemd}
%config(noreplace) %attr(0644,tomcat,nobody) /usr/lib/systemd/system/tomcat.service
%else
%attr(0755,tomcat,nobody) /etc/init.d/ea-tomcat85
%endif

%changelog
* Thu Jan 18 2018 Dan Muey <dan@cpanel.net> - 8.5.24-1
- ZC-3244: Initial ea-tomcat85 (v8.5.24)
