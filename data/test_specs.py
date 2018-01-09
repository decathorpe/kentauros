TEST_SPEC_GIT_SOURCE = """# RPM .spec file for testing with git sources 
Name:           testpackage
Summary:        Test Package
Version:        0
Release:        1%{?dist}
License:        Public Domain

URL:            https://github.com/decathorpe/kentauros
Source0:        %{name}-%{version}.tar.gz

%description
Test Package

%prep
%autosetup

%build

%install

%changelog

"""

TEST_SPEC_URL_SOURCE = """# RPM .spec file for testing with url sources 
Name:           testpackage
Summary:        Test Package
Version:        1.0
Release:        1%{?dist}
License:        Public Domain

URL:            https://github.com/decathorpe/kentauros
Source0:        https://decathorpe.com/archive/%{name}/%{version}/%{name}-%{version}.tar.gz

%description
Test Package

%prep
%autosetup

%build

%install

%changelog

"""

TEST_SPEC_LOCAL_SOURCE = """# RPM .spec file for testing with local sources 
Name:           testpackage
Summary:        Test Package
Version:        0
Release:        1%{?dist}
License:        Public Domain

URL:            https://github.com/decathorpe/kentauros
Source0:        %{name}-%{version}.tar.gz

%description
Test Package

%prep
%autosetup

%build

%install

%changelog

"""
