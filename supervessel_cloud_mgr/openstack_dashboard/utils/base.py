from random import Random

__author__ = 'yuehaitao'


def random_string(prefix='i', postfix='', randomlength=9):
    post_fix = ''
    chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
    length = len(chars) - 1
    random = Random()

    for i in range(randomlength):
        post_fix += chars[random.randint(0, length)]

    return prefix + '-' + post_fix + postfix
