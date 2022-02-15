from ast import keyword
from tokenize import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import BasePermission

class AdminAuthentication(TokenAuthentication):
    keyword = 'Bearer'

class SuperAdminPermission(BasePermission):
	def has_permission(self,request,view):
		return bool(request.user and request.user.is_authenticated and request.user.is_superuser and request.user.is_active)

class AdminPermission(BasePermission):

	def has_perission(self,request,view):
		return bool(request.user and request.user.is_authenticated and request.user.is_staff and request.user.is_active)