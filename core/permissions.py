from rest_framework.permissions import BasePermission

from .models import GRADE_LEVEL


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.account_type in {'md', 'admin'}


class IsSiteEngineer(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.grade == 'tech_se'


class IsSubcontractor(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.grade == 'tech_sc'


class MinimumGradePermission(BasePermission):
    minimum_level = 0

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.authority_level >= self.minimum_level


def MinimumGrade(grade):
    class _MinimumGrade(MinimumGradePermission):
        minimum_level = GRADE_LEVEL.get(grade, 0)

    return _MinimumGrade


class AccountTypePermission(BasePermission):
    allowed_accounts = set()

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.account_type in self.allowed_accounts


def AccountOnly(*accounts):
    class _AccountOnly(AccountTypePermission):
        allowed_accounts = set(accounts)

    return _AccountOnly
