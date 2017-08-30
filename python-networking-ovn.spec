%global drv_vendor OVN
%global pkgname networking-ovn
%global srcname networking_ovn
%global docpath doc/build/html

%{!?upstream_version: %global upstream_version %{version}%{?milestone}}

Name:           python-%{pkgname}
Version:        3.0.0
Release:        1%{?dist}
Summary:        %{drv_vendor} OpenStack Neutron driver

License:        ASL 2.0
URL:            https://pypi.python.org/pypi/%{pkgname}
Source0:        https://tarballs.openstack.org/%{pkgname}/%{pkgname}-%{upstream_version}.tar.gz

#

BuildArch:      noarch
BuildRequires:  git
BuildRequires:  python2-devel
BuildRequires:  python-debtcollector
BuildRequires:  python-mock

# This is required to generate the networking-ovn.ini configuration file
BuildRequires:  python-neutron

BuildRequires:  python-oslo-config
BuildRequires:  python-oslo-log
BuildRequires:  python-openstackdocstheme
BuildRequires:  python-pbr
BuildRequires:  python-sphinx


# python-openvswitch is not included in openstack-neutron-common.
# Its needed by networking-ovn.
Requires:       openstack-neutron-common
Requires:       python-babel
Requires:       python-netaddr
Requires:       python-neutron-lib >= 1.9.0
Requires:       python-oslo-config >= 2:4.0.0
Requires:       python-openvswitch >= 2.7.0
Requires:       python-pbr
Requires:       python-six
Requires:       python-tenacity
Requires:       python-ovsdbapp >= 0.4.0
Requires:       pyOpenSSL >= 0.14

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
rm -rf %{docpath}/.{doctrees,buildinfo}

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
%{_bindir}/networking-ovn-metadata-agent
%config(noreplace) %attr(0640, root, neutron) %{_sysconfdir}/neutron/plugins/networking-ovn/*.ini


%changelog
* Wed Aug 30 2017 rdo-trunk <javier.pena@redhat.com> 3.0.0-1
- Update to 3.0.0

* Fri Aug 25 2017 Alfredo Moralejo <amoralej@redhat.com> 3.0.0-0.1.0rc2
- Update to 3.0.0.0rc2

* Thu Sep 29 2016 Haikel Guemar <hguemar@fedoraproject.org> 1.0.0-0.3.0rc1
- Update to 1.0.0.0rc2

* Wed Sep 21 2016 Alfredo Moralejo <amoralej@redhat.com> 1.0.0-0.2.0rc1
- Update to 1.0.0.0rc1

* Wed Sep 14 2016 Haikel Guemar <hguemar@fedoraproject.org> 1.0.0-0.1.0b3
- Update to 1.0.0.0b3
