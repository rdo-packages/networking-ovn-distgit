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
Source0:        https://tarballs.openstack.org/%{pkgname}/%{pkgname}-%{upstream_version}.tar.gz
Source1:        networking-ovn-metadata-agent.service
#

BuildArch:      noarch
BuildRequires:  git
BuildRequires:  python2-devel
BuildRequires:  python2-debtcollector
BuildRequires:  python2-mock
BuildRequires:  openstack-macros

# This is required to generate the networking-ovn.ini configuration file
BuildRequires:  python-neutron

BuildRequires:  python2-oslo-config
BuildRequires:  python2-oslo-log
BuildRequires:  python2-openstackdocstheme
BuildRequires:  python2-ovsdbapp
BuildRequires:  python2-pbr
BuildRequires:  python2-sphinx


# python-openvswitch is not included in openstack-neutron-common.
# Its needed by networking-ovn.
Requires:       openstack-neutron-common
Requires:       python2-babel
Requires:       python2-futurist >= 1.2.0
Requires:       python2-netaddr
Requires:       python2-neutron-lib >= 1.18.0
Requires:       python2-oslo-config >= 2:5.2.0
Requires:       python2-openvswitch >= 2.8.0
Requires:       python2-pbr
Requires:       python2-six
Requires:       python2-tenacity
Requires:       python2-ovsdbapp >= 0.10.0
Requires:       python2-pyOpenSSL >= 17.1.0
Requires:       python2-sqlalchemy >= 1.2.0

%description
OVN provides virtual networking for Open vSwitch and is a component of the
Open vSwitch project.

This package contains %{drv_vendor} networking driver which provides
integration between OpenStack Neutron and OVN.


%package metadata-agent
Summary:        networking-ovn metadata agent
BuildRequires:  systemd
Requires:       python-%{pkgname} = %{version}-%{release}
Requires:       openvswitch >= 2.8.0
%{?systemd_requires}

%description metadata-agent
OVN provides virtual networking for Open vSwitch and is a component of the
Open vSwitch project.

This package contains the agent that implements the metadata proxy so that VM's
can retrieve metadata from OpenStack Nova.

%package migration-tool
Summary:        networking-ovn ML2/OVS to OVN migration tool
Requires:       python-%{pkgname} = %{version}-%{release}

%description migration-tool
This package provides the necessary tools to update an existing ML2/OVS
OpenStack to OVN based backend.

%prep
%autosetup -n %{pkgname}-%{upstream_version} -S git

# Let's handle dependencies ourselves
%py_req_cleanup

# Kill egg-info in order to generate new SOURCES.txt
rm -rf {srcname}.egg-info


%build
export SKIP_PIP_INSTALL=1
%{__python2} setup.py build
%{__python2} setup.py build_sphinx
rm -rf %{docpath}/.{doctrees,buildinfo}

# Generate config file
PYTHONPATH=. oslo-config-generator --namespace networking_ovn --output-file networking-ovn.ini
PYTHONPATH=. oslo-config-generator --namespace networking_ovn.metadata.agent --output-file networking-ovn-metadata-agent.ini


%install
%{__python2} setup.py install -O1 --skip-build --root %{buildroot}

# Remove unused files
rm -rf %{buildroot}%{python2_sitelib}/bin
rm -rf %{buildroot}%{python2_sitelib}/doc
rm -rf %{buildroot}%{python2_sitelib}/tools


# Move config file to proper location
install -d -m 755 %{buildroot}%{_sysconfdir}/neutron/plugins/networking-ovn
mv networking-ovn.ini %{buildroot}%{_sysconfdir}/neutron/plugins/networking-ovn
mv networking-ovn-metadata-agent.ini %{buildroot}%{_sysconfdir}/neutron/plugins/networking-ovn
chmod 640 %{buildroot}%{_sysconfdir}/neutron/plugins/*/*.ini

# Create configuration directories for all services that can be populated by users with custom *.conf files
mkdir -p %{buildroot}/%{_sysconfdir}/neutron/conf.d/networking-ovn-metadata-agent

# Install systemd units
install -p -D -m 644 %{SOURCE1} %{buildroot}%{_unitdir}/networking-ovn-metadata-agent.service

%post metadata-agent
%systemd_post networking-ovn-metadata-agent.service


%preun metadata-agent
%systemd_preun networking-ovn-metadata-agent.service


%postun metadata-agent
%systemd_postun_with_restart networking-ovn-metadata-agent.service

%files
%license LICENSE
%doc %{docpath}
%{python2_sitelib}/%{srcname}
%{python2_sitelib}/%{srcname}-*.egg-info
%{_bindir}/neutron-ovn-db-sync-util
%dir %{_sysconfdir}/neutron/plugins/networking-ovn
%config(noreplace) %attr(0640, root, neutron) %{_sysconfdir}/neutron/plugins/networking-ovn/networking-ovn.ini

%files metadata-agent
%license LICENSE
%{_bindir}/networking-ovn-metadata-agent
%{_unitdir}/networking-ovn-metadata-agent.service
%config(noreplace) %attr(0640, root, neutron) %{_sysconfdir}/neutron/plugins/networking-ovn/networking-ovn-metadata-agent.ini
%dir %{_sysconfdir}/neutron/conf.d/networking-ovn-metadata-agent

%files migration-tool
%license LICENSE
%{_bindir}/networking-ovn-migration-mtu
%{_bindir}/ovn_migration.sh
%{_datadir}/ansible/networking-ovn-migration/playbooks/

%changelog
