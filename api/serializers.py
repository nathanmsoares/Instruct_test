import json
from typing import List
from rest_framework import serializers
from django.http import HttpResponse, JsonResponse
from rest_framework.exceptions import ParseError
from .models import PackageRelease, Project
from .checker import PackageChecker
from collections import OrderedDict


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
        # TODO
        # - Processar os pacotes recebidos
        # - Persistir informações no banco
        packages: List = validated_data['packages']
        print("packages", packages)
        print("type packages", type(packages))
        packages: List = \
            PackageChecker.checking_packages(
                packages)
        create_project = Project.objects.create(name=validated_data["name"])
        print(create_project.id)
        for i in packages:
            package = PackageRelease.objects.create(
                **i, project=create_project)
            print(package.id)
        return create_project

    def update(self, instance, validated_data):
        pass
        related_packages = PackageRelease.objects.filter(project=instance.id)
        # print(related_packages.filter(name="Django"))  # Deletar
        print(related_packages)
        # TODO: Improve to handle objects in code so it will not be necessary
        #       to execute more DB queries more than necessary
        # ordered_dict_list = []
        # for i in related_packages:
        #     ordered_dict: OrderedDict = OrderedDict({"name": i.name.upper(
        #     ), "version": i.version, "id": i.id, "in_validated_data": False,
        #         "same_version": False})
        #     ordered_dict_list.append(ordered_dict)
        # for i in range(len(ordered_dict_list)):
        #     for k in validated_data['packages']:
        #         print(ordered_dict_list[i]['name'])
        #         print(k['name'])
        #         if ordered_dict_list[i]['name'] == k['name'].upper():
        #             ordered_dict_list[i]['in_validated_data'] = True
        #             if ordered_dict_list[i]['version'] == k['version']:
        #                 ordered_dict_list[i]['same_version'] = True
        #                 break
        #             else:
        #                 ordered_dict_list[i]['same_version'] = False
        #                 break
        if self.context['request'].method == "PUT":
            # packages_dict = {package in for package in related_packages}
            if instance.name != validated_data['name']:
                instance.name = validated_data['name']
                instance.save()
            # The next lines and for will check if the received packages are
            # already in the DB and check the versions if they are the same.
            # if they are not, the version will be checked. If the version
            # does not exist, a 400 error will rise.
            upgrade_data_if_success = []
            deleted_packages = 0
            for i in range(len(validated_data["packages"])):
                try:
                    print(validated_data["packages"])
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
                        # package.delete()
                    # if empty turn pop
                    print(type(package))
                except ParseError as e:
                    print(e)
                    if e.detail['error'].code == 'parse_error':
                        raise ParseError(
                            {"error": "One or more packages doesn't exist"})
                except Exception as e:
                    print(e)
            # print(validated_data["packages"])
            if validated_data["packages"]:
                packages: List = \
                    PackageChecker.checking_packages(
                        validated_data["packages"])
                for i in packages:
                    PackageRelease.objects.create(**i, project=instance)

            for i in upgrade_data_if_success:
                package = PackageRelease.objects.get(
                    name=i['name'])
                package.version = i['version']
                package.save()
            return instance

        elif self.context['request'].method == "PATCH":
            for package in related_packages:
                print(package.name)

        print(instance.id)
        # for package in related_packages:
        #     print(package.name)
        # print(instance.packages)
        print(validated_data)
        # PackageChecker.checking_packages(validated_data['packages'])
        print("type", type(validated_data))
        print("entrou aqui")
        print("instancia", instance)
        print("validated_data", validated_data)
        return instance

    # def to_representation(self, instance):
        # ret = super(ProjectSerializer, self).to_representation(instance)
        # # check the request is list view or detail view
        # is_list_view = isinstance(self.instance, list)
        # extra_ret = {'key': 'list value'} if is_list_view else {
        #     'key': 'single value'}
        # ret.update(extra_ret)
        # return {"teste": "teste"}
