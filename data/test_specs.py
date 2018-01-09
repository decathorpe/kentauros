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
