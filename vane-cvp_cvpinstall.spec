#################################
# Application specific settings #
#################################
%global cvpi_base      /cvpi
%global cvpapps_root   %{cvpi_base}/apps
%global cvpconf_root   %{cvpi_base}/conf
%global cvpdocker_root %{cvpi_base}/docker
%global app_root       %{cvpapps_root}/vane-cvp
%global app_logs       %{app_root}/logs
%global app_shared    %{app_root}/vane-data

Name: vane-cvp
Version: Replaced_by_make
Release: Replaced_by_make
Summary: Vane and CVP extension

Group: Development/Libraries
License: BSD-3-Clause
URL: http://www.arista.com
Source0: %{name}-%{version}-%{release}.tar.gz

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
Requires:  cvpi

%description
The Vane module contains Vane running in a container on CVP.

%prep
%setup -q -n %{name}-%{version}-%{release}

%install
rm -rf %{buildroot}
%{__install} -m 0755 -d %{buildroot}%{app_logs}
%{__install} -m 0755 -d %{buildroot}%{app_logs}/rotated
%{__install} -m 0777 -d %{buildroot}%{app_shared}
%{__install} -m 0755 -d %{buildroot}%{cvpconf_root}/components
%{__install} -m 0755 -d %{buildroot}%{cvpconf_root}/disabled-components
%{__install} -m 0755 -d %{buildroot}%{cvpconf_root}/kubernetes
%{__install} -m 0755 -d %{buildroot}%{cvpdocker_root}

%{__install} -m 0644 cvpi/conf/components/vane-cvp* %{buildroot}%{cvpconf_root}/components
%{__install} -m 0644 cvpi/conf/disabled-components/vane-cvp* %{buildroot}%{cvpconf_root}/disabled-components
%{__install} -m 0644 cvpi/conf/kubernetes/vane-cvp* %{buildroot}%{cvpconf_root}/kubernetes
%{__install} -m 0644 cvpi/docker/vane-cvp.tar.gz %{buildroot}%{cvpdocker_root}/
%{__install} -m 0644 cvpi/apps/vane-cvp/logs/.keep %{buildroot}%{app_logs}/
%{__install} -m 0644 cvpi/apps/vane-cvp/logs/rotated/.keep %{buildroot}%{app_logs}/rotated/
exit 0

%files
%defattr(-,root,root,-)
%defattr(-,cvp,cvp,-)
%dir %{app_root}
%dir %{app_logs}
%{app_logs}/.keep
%dir %{app_logs}/rotated
%{app_logs}/rotated/.keep
%dir %{app_shared}
%{cvpconf_root}/components/vane-cvp.*
%{cvpconf_root}/disabled-components/vane-cvp*
%{cvpconf_root}/kubernetes/vane-cvp.yaml
%{cvpdocker_root}/vane-cvp.tar.gz

%pre
# pre install of new package
# Not executed during an uninstallation
# $1 == 1 - install
# $1 >= 2 - upgrade
exit 0

%post
# post install of new package.
# Not executed during an uninstallation
# $1 == 1 - install
# $1 >= 2 - upgrade
exit 0

%preun
# preun of old package
# $1 == 0 - uninstall
# $1 == 1 - upgrade
exit 0

%postun
# postun of old package
# $1 == 0 - uninstall
# $1 == 1 - upgrade
exit 0

%clean
rm -rf %{buildroot}
