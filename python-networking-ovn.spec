%global milestone .0rc2
%global drv_vendor OVN
%global pkgname networking-ovn
%global srcname networking_ovn
%global docpath doc/build/html

%{!?upstream_version: %global upstream_version %{version}%{?milestone}}

Name:           python-%{pkgname}
Version:        1.0.0
Release:        0.3%{?milestone}%{?dist}
Summary:        %{drv_vendor} OpenStack Neutron driver

License:        ASL 2.0
URL:            https://pypi.python.org/pypi/%{pkgname}
Source0:        https://tarballs.openstack.org/%{pkgname}/%{pkgname}-%{upstream_version}.tar.gz

#
# patches_base=1.0.0.0rc2
#

BuildArch:      noarch
BuildRequires:  python2-devel
BuildRequires:  python-debtcollector
BuildRequires:  python-mock


BuildRequires:  python-oslo-config
BuildRequires:  python-oslo-log
BuildRequires:  python-oslo-sphinx
BuildRequires:  python-pbr
BuildRequires:  python-setuptools
BuildRequires:  python-sphinx


# python-openvswitch is not included in openstack-neutron-common.
# Its needed by networking-ovn.
# networking-ovn is an ml2 plugin, so it requires openstack-neutron-ml2.
Requires:       openstack-neutron-common
Requires:       openstack-neutron-ml2
Requires:       python-babel
Requires:       python-netaddr
Requires:       python-neutron-lib >= 1.1.0
Requires:       python-oslo-config >= 2:3.14.0
Requires:       python-openvswitch >= 2.6.1
Requires:       python-pbr
Requires:       python-retrying
Requires:       python-six
Requires:       python-tenacity

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


%install
%{__python2} setup.py install -O1 --skip-build --root %{buildroot}

# Remove unused files
rm -rf %{buildroot}%{python2_sitelib}/bin
rm -rf %{buildroot}%{python2_sitelib}/doc
rm -rf %{buildroot}%{python2_sitelib}/tools



%files
%license LICENSE
%doc %{docpath}
%{python2_sitelib}/%{srcname}
%{python2_sitelib}/%{srcname}-*.egg-info
%{_bindir}/neutron-ovn-db-sync-util


%changelog
* Thu Sep 29 2016 Haikel Guemar <hguemar@fedoraproject.org> 1.0.0-0.3.0rc1
- Update to 1.0.0.0rc2

* Wed Sep 21 2016 Alfredo Moralejo <amoralej@redhat.com> 1.0.0-0.2.0rc1
- Update to 1.0.0.0rc1

* Wed Sep 14 2016 Haikel Guemar <hguemar@fedoraproject.org> 1.0.0-0.1.0b3
- Update to 1.0.0.0b3

