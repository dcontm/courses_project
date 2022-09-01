import string
import random
from django.core.exceptions import ValidationError
from django.utils.encoding import force_text




def validate_avatar(avatar):

	file_size = avatar.file.size
	limit_size = 1024*1024*4		#4mb
	if file_size > limit_size:
		raise ValidationError("Максимальный размер файла 5 МБ")



def path_avatar(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'avatars/user_{0}/{1}'.format(instance.id, filename)


def generate_code(size=6, chars=string.ascii_letters+string.digits):
	return ''.join(random.choice(chars) for i in range(size))