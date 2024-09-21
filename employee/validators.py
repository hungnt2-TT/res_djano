import os

from django.core.exceptions import ValidationError


def validator_file_upload(value):
    print('value.size')
    ext = os.path.splitext(value.name)[1]
    valid_extensions = ['.jpg', '.jpeg', '.png']
    print('value.size', value.size)
    if not ext.lower() in valid_extensions:
        raise ValidationError('Unsupported file extension.' + str(valid_extensions))
    if value.size > 10 * 1024 * 1024:
        raise ValidationError('File size should not exceed 10 MB.')
    return value
