from typing import List, OrderedDict
import requests
from rest_framework.exceptions import ParseError
from .logger import logger


class PackageChecker():

    @staticmethod
    def checking_packages(package_names: List) -> \
            List[OrderedDict]:
        logger.debug(
            "[Checker] Checking if theses packages and their versions exist" +
            f"{package_names}")
        error_case_dict = {"error": "One or more packages doesn't exist"}
        checked_packages: List[OrderedDict] = []
        for package in package_names:
            response = requests.get(
                f"https://pypi.org/pypi/{package['name']}/json")
            if response.status_code != 200:
                logger.debug(f"[Checker] {package['name']} does not exist")
                raise ParseError(error_case_dict)
            else:
                package_versions = list(response.json()['releases'].keys())
                if package.get("version") is None:
                    package['version'] = package_versions[-1]
                    checked_packages.append(package)
                    continue
                elif package['version'] not in package_versions:
                    logger.debug(
                        f"[Checker] version {package['version']} of" +
                        f"{package['name']} does not exist")
                    raise ParseError(error_case_dict)
                else:
                    logger.debug(f"[Checker] Adding {package} to the list")
                    checked_packages.append(package)
        logger.debug(
            f"[Checker] Returning checked packages {checked_packages}")
        return checked_packages
