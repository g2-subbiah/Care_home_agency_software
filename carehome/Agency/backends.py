# yourapp/backends.py
# backends.py
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()

class GroupBasedBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, group=None, **kwargs):
        try:
            user = User.objects.get(username=username)
            if user.check_password(password) and user.groups.filter(name=group).exists():
                return user
        except User.DoesNotExist:
            return None



# from django.contrib.auth.backends import BaseBackend
# from django.contrib.auth.models import User

# class GroupBasedBackend(BaseBackend):
#     def authenticate(self, request, username=None, password=None, group=None):
#         try:
#             user = User.objects.get(username=username)
#             if user.check_password(password) and user.groups.filter(name=group).exists():
#                 return user
#         except User.DoesNotExist:
#             return None
#         return None

#     def get_user(self, user_id):
#         try:
#             return User.objects.get(pk=user_id)
#         except User.DoesNotExist:
#             return None

