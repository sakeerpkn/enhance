from rest_framework.permissions import BasePermission


class GroupRequiredPermission(BasePermission):
    group_name = ""

    def has_permission(self, request, view):
        return request.user.groups.filter(name="Process manager")


class ProcessManagerGroupRequired(GroupRequiredPermission):
    group_name = "Process manager"
