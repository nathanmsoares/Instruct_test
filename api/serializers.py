from typing import List
from rest_framework import serializers
from rest_framework.exceptions import ParseError
from .models import PackageRelease, Project
from .components.checker import PackageChecker
from collections import OrderedDict
from .components.logger import logger


class PackageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PackageRelease
        fields = ['name', 'version']
        extra_kwargs = {'version': {'required': False}}


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['name', 'packages']

    packages = PackageSerializer(many=True)

    def create(self, validated_data):
        logger.debug(
            f"[Serializers] Creating an new Project. Project: {validated_data}"
        )
        packages: List = validated_data['packages']
        packages: List = \
            PackageChecker.checking_packages(
                packages)
        create_project = Project.objects.create(name=validated_data["name"])
        for i in packages:
            PackageRelease.objects.create(
                **i, project=create_project)
        logger.debug(
            f"[Serializers] Project created. Project: {validated_data}"
        )
        return create_project

    def update(self, instance, validated_data):
        if self.context['request'].method == "PUT":
            logger.debug(
                f"[Serializers] Method PUT, inserting {validated_data} on DB")
            # The next lines and for will check if the received packages are
            # already in the DB and check the versions if they are the same.
            # if they are not, the version will be checked. If the version
            # does not exist, a 400 error will rise.
            upgrade_data_if_success = []
            deleted_packages = 0
            for i in range(len(validated_data["packages"])):
                try:
                    logger.debug(
                        f"[Serializers] Checking if {instance.name}'s" +
                        " packages' versions the versions received are " +
                        "the same")
                    package = PackageRelease.objects.get(
                        name=validated_data["packages"][i-deleted_packages]
                        ['name'])
                    if package.version == \
                            validated_data["packages"][i-deleted_packages][
                                'version']:
                        del validated_data["packages"][i-deleted_packages]
                        deleted_packages += 1
                    else:
                        packages: List = \
                            PackageChecker.checking_packages(
                                [validated_data["packages"]
                                 [i-deleted_packages]])
                        del validated_data["packages"][i-deleted_packages]
                        deleted_packages += 1
                        upgrade_data_if_success.extend(packages)
                except ParseError as e:
                    if e.detail['error'].code == 'parse_error':
                        raise ParseError(
                            {"error": "One or more packages doesn't exist"})
                except Exception as e:
                    logger.warning(
                        f"Something unexpected happened, check error {e}")
            if validated_data["packages"]:
                packages: List = \
                    PackageChecker.checking_packages(
                        validated_data["packages"])
                for i in packages:
                    PackageRelease.objects.create(**i, project=instance)

            for i in upgrade_data_if_success:
                logger.debug(f"Every Package is ok. Adding {i}")
                package = PackageRelease.objects.get(
                    name=i['name'])
                package.version = i['version']
                package.save()
            if instance.name != validated_data['name']:
                instance.name = validated_data['name']
                instance.save()
            return instance

        elif self.context['request'].method == "PATCH":
            if "packages" in validated_data:
                new_packages: List[OrderedDict] = []
                old_packages: List[OrderedDict] = []
                for i in validated_data["packages"]:
                    if not ("name" in i.keys()):
                        logger.debug("There is no name on the package")
                        raise ParseError(
                            {"error": "One or more packages doesn't exist"})
                    try:
                        package = PackageRelease.objects.get(name=i['name'])
                        if not ('version' in i.keys()) or \
                                i['version'] != package.version:
                            old_packages.append(i)
                    except Exception as e:
                        logger.debug(
                            f"[Serializer] Adding {i['name']} to 'new_packages'")
                        new_packages.append(i)
                if new_packages or old_packages:
                    packages_new = []
                    packages_old = []
                    if new_packages:
                        packages_new: List[OrderedDict] = \
                            PackageChecker.checking_packages(new_packages)
                    if old_packages:
                        packages_old: List[OrderedDict] = \
                            PackageChecker.checking_packages(old_packages)
                    if packages_new:
                        logger.debug(
                            "[Serializer] Adding new packages" +
                            f"to {instance.name}")
                        for i in packages_new:
                            PackageRelease.objects.create(
                                **i, project=instance)
                    if packages_old:
                        logger.debug("Changing packages' version")
                        for i in packages_old:
                            package = PackageRelease.objects.get(
                                name=i['name'])
                            package.version = i['version']
                            package.save()
            if 'name' in validated_data and \
                    validated_data['name'] != instance.name:
                logger.debug(
                    "[Serializer] updating instance's name from" +
                    f"{instance.name} to {validated_data['name']}")
                instance.name = validated_data['name']
                instance.save()
            return instance
