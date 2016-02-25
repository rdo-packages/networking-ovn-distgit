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

# This is required to generate the networking-ovn.ini configuration file
BuildRequires:  python-neutron

BuildRequires:  python-oslo-config
BuildRequires:  python-oslo-log
BuildRequires:  python-oslo-sphinx
BuildRequires:  python-pbr
BuildRequires:  python-sphinx


# python-openvswitch is not included in openstack-neutron-common.
# Its needed by networking-ovn.
Requires:       openstack-neutron-common
Requires:       python-openvswitch


%description
OVN provides virtual networking for Open vSwitch and is a component of the
Open vSwitch project.

This package contains %{drv_vendor} networking driver which provides
integration between OpenStack Neutron and OVN.


%prep
%autosetup -n %{pkgname}-%{upstream_version} -S git

# Let's handle dependencies ourselves
rm -f requirements.txt test-requirements.txt

# Kill egg-info in order to generate new SOURCES.txt
rm -rf {srcname}.egg-info


%build
export SKIP_PIP_INSTALL=1
%{__python2} setup.py build
%{__python2} setup.py build_sphinx
rm %{docpath}/.buildinfo

# Generate config file
PYTHONPATH=. oslo-config-generator --namespace networking_ovn --output-file networking-ovn.ini


%install
%{__python2} setup.py install -O1 --skip-build --root %{buildroot}

# Remove unused files
rm -rf %{buildroot}%{python2_sitelib}/bin
rm -rf %{buildroot}%{python2_sitelib}/doc
rm -rf %{buildroot}%{python2_sitelib}/tools


# Move config file to proper location
install -d -m 755 %{buildroot}%{_sysconfdir}/neutron/plugins/networking-ovn
mv networking-ovn.ini %{buildroot}%{_sysconfdir}/neutron/plugins/networking-ovn
chmod 640 %{buildroot}%{_sysconfdir}/neutron/plugins/*/*.ini


%files
%license LICENSE
%doc %{docpath}
%{python2_sitelib}/%{srcname}
%{python2_sitelib}/%{srcname}-*.egg-info
%{_bindir}/neutron-ovn-db-sync-util
%config(noreplace) %attr(0640, root, neutron) %{_sysconfdir}/neutron/plugins/networking-ovn/*.ini
