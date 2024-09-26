from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
import logging

logger = logging.getLogger(__name__)

class PhoneBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        User = get_user_model()
        try:
            user = User.objects.get(phone_number=username)
            if user.check_password(password):
                logger.debug(f"User {username} authenticated successfully")
                return user
        except User.DoesNotExist:
            logger.debug(f"User {username} not found")
            return None
        except Exception as e:
            logger.error(f"Error authenticating user {username}: {e}")
            return None

    def get_user(self, user_id):
        User = get_user_model()
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None