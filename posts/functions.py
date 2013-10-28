from django.utils.translation import ugettext, ungettext
import random


def split_and_random_list(list, limit):
    new_list = []
    count_list = len(list)
    for number in xrange(limit):
        count_list -= 1
        random_nb = random.randint(0, count_list)
        new_list.append(list[random_nb])
        list[random_nb], list[count_list] = list[count_list], list[random_nb]
    return new_list


def show_first_items(list, limit=2, sep=', '):
    if len(list) > limit:
        nb_others = len(list) - limit
        items = split_and_random_list(list, limit)
        return ungettext('%(items)s and %(count)d other',
                         '%(items)s and %(count)d others', nb_others) %
                         {'items': sep.join(items), 'count': nb_others}
    elif len(list) == 2:
        return ' %s '.join(list) % ugettext('and')
    else:
        return sep.join(list)
