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
%define release_prefix 2
Release: %{release_prefix}%{?dist}.cpanel
License: Apache License, 2.0
Group:   System Environment/Daemons
URL: http://tomcat.apache.org/
Source0: http://www-eu.apache.org/dist/tomcat/tomcat-8/v8.5.24/bin/apache-tomcat-8.5.24.tar.gz
Source1: setenv.sh
Source2: ea-tomcat85.logrotate
Source3: ea-tomcat85.service
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
%setup -qn apache-tomcat-%{version}

%pre
# if the user already exists, just add to nobody group
if [ `/usr/bin/getent passwd tomcat` ];
    then usermod -G nobody tomcat;
# if the user didn't exist lets check the group to give useradd the right flags
# in case there is a tomcat group leftover from who knows what...
elif [ `/usr/bin/getent group tomcat` ];
then /usr/sbin/useradd -r -d /opt/cpanel/%{name} -s /sbin/nologin -g tomcat -G nobody tomcat
else
# otherwise lets just create the user like normal
/usr/sbin/useradd -r -d /opt/cpanel/%{name} -s /sbin/nologin -G nobody tomcat
fi

# Just ensuring in some rare case group tomcat wasnt created we check here
/usr/bin/getent group tomcat || /usr/sbin/groupadd -r tomcat

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
cp %{SOURCE3} $RPM_BUILD_ROOT%{_unitdir}/ea-tomcat85.service
%else
mkdir -p $RPM_BUILD_ROOT%{_initddir}
cp %{SOURCE4} $RPM_BUILD_ROOT%{_initddir}/%{name}
%endif

%clean
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf %{buildroot}

%post

# stop and start, there is no restart
if [ -e "/var/run/catalina.pid" ]; then
%if %{with_systemd}
systemctl stop ea-tomcat85
systemctl disable ea-tomcat85
systemctl daemon-reload
%else
/opt/cpanel/ea-tomcat85/bin/shutdown.sh
%endif
fi

%if %{with_systemd}
systemctl enable ea-tomcat85
systemctl daemon-reload
systemctl start ea-tomcat85
%else
/opt/cpanel/ea-tomcat85/bin/startup.sh
%endif

%preun

# checking the pid file helps avoid scary sounding warnings like:
#   $CATALINA_PID was set but the specified file does not exist. Is Tomcat running? Stop aborted.
if [ -e "/var/run/catalina.pid" ]; then
%if %{with_systemd}
systemctl stop ea-tomcat85
systemctl disable ea-tomcat85
systemctl daemon-reload
%else
/opt/cpanel/ea-tomcat85/bin/shutdown.sh
%endif
fi

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

%files
%defattr(-,tomcat,nobody,-)
/opt/cpanel/ea-tomcat85
%config(noreplace) %attr(0755,tomcat,nobody) /opt/cpanel/ea-tomcat85/bin/setenv.sh
%dir /var/log/ea-tomcat85
%ghost %attr(0644,tomcat,nobody) /var/run/catalina.pid
/etc/logrotate.d/ea-tomcat85
%if %{with_systemd}
# Must be root root here for write permissions
%config(noreplace) %attr(0644,root,root) %{_unitdir}/ea-tomcat85.service
%else
%attr(0755,tomcat,nobody) %{_initddir}/ea-tomcat85
%endif

%changelog
* Wed Mar 14 2018 Cory McIntire <cory@cpanel.net> - 8.5.24-2
- EA-7297: Fix rpmlint errors and warnings
- Credit: https://github.com/dkasyanov

* Thu Jan 18 2018 Dan Muey <dan@cpanel.net> - 8.5.24-1
- ZC-3244: Initial ea-tomcat85 (v8.5.24)
