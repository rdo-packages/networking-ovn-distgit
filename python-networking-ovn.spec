%global drv_vendor OVN
%global pkgname networking-ovn
%global srcname networking_ovn
%global docpath doc/build/html

%{!?upstream_version: %global upstream_version %{version}%{?milestone}}

Name:           python-%{pkgname}
Version:        XXX
Release:        XXX
Summary:        %{drv_vendor} OpenStack Neutron driver

License:        ASL 2.0
URL:            https://pypi.python.org/pypi/%{pkgname}
Source0:        https://pypi.python.org/packages/source/n/%{pkgname}/%{pkgname}-%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  python2-devel
BuildRequires:  python-debtcollector
BuildRequires:  python-mock
BuildRequires:  python-oslo-config
BuildRequires:  python-oslo-sphinx
BuildRequires:  python-pbr
BuildRequires:  python-setuptools
BuildRequires:  python-sphinx
BuildRequires:  python-testrepository
BuildRequires:  python-testtools
BuildRequires:  python-webtest

Requires:       openstack-neutron-common
Requires:       python-babel
Requires:       python-pbr


%description
This package contains %{drv_vendor} networking driver for OpenStack Neutron.


%prep
%setup -q -n %{pkgname}-%{upstream_version}


%build
rm requirements.txt test-requirements.txt
%{__python2} setup.py build
%{__python2} setup.py build_sphinx
rm %{docpath}/.buildinfo

# Generate config file
oslo-config-generator --namespace networking_ovn --output-file networking-ovn.ini

#%check
#%{__python2} setup.py testr


%install
export PBR_VERSION=%{version}
export SKIP_PIP_INSTALL=1
%{__python2} setup.py install --skip-build --root %{buildroot}

# Move config file to proper location
install -d -m 755 %{buildroot}%{_sysconfdir}/neutron/plugins/networking-ovn
mv networking-ovn.ini %{buildroot}%{_sysconfdir}/neutron/plugins/networking-ovn
chmod 640 %{buildroot}%{_sysconfdir}/neutron/plugins/*/*.ini


%files
%license LICENSE
%doc %{docpath}
%{python2_sitelib}/%{srcname}
%{python2_sitelib}/%{srcname}-%{version}-py%{python2_version}.egg-info
%{_bindir}/neutron-ovn-db-sync-util
%config(noreplace) %attr(0640, root, neutron) %{_sysconfdir}/neutron/plugins/networking-ovn/*.ini
