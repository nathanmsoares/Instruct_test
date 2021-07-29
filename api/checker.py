from typing import List, OrderedDict
import requests
from rest_framework.exceptions import ParseError


class PackageChecker():

    @staticmethod
    def checking_packages(package_names: List) -> \
            List[OrderedDict]:
        error_case_dict = {"error": "One or more packages doesn't exist"}
        checked_packages: List[OrderedDict] = []
        for package in package_names:
            print(checked_packages)
            response = requests.get(
                f"https://pypi.org/pypi/{package['name']}/json")
            if response.status_code != 200:
                raise ParseError(error_case_dict)
            else:
                package_versions = list(response.json()['releases'].keys())
                if package.get("version") is None:
                    package['version'] = package_versions[-1]
                    print(package_versions)
                    print(type(package_versions))
                    checked_packages.append(package)
                    continue
                elif package['version'] not in package_versions:
                    raise ParseError(error_case_dict)
                else:
                    checked_packages.append(package)
        print(checked_packages)
        print(response.status_code)
        print(type(response))
        return checked_packages
