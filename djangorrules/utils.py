from django.utils.translation import gettext_lazy as _


def join_with_conjunction(value_list, conjunction='and'):
    last = ''
    if len(value_list) > 1:
        last = f" {conjunction} {value_list[-1]}"
        value_list = value_list[:-1]
    items = _(', '.join(str(value) for value in value_list) + last)
    return items
