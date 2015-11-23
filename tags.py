import re
import globals

# Get list of tag names
def getTags (repo):
    tags = []
    try:
        for tag in globals.cache.getTags(repo):
            tags.append(tag.name)
    except TypeError:
        # PyGithub issue #278: Iterating through repo.get_tags() throws
        # NoneType TypeError for repositories with lots of tags:
        # https://github.com/jacquev6/PyGithub/issues/278
        print "ERROR: PyGithub threw a TypeError while iterating through tags"
    tags.sort(key=tagSortKey, reverse=True)

    if (not tags) or (len(tags) < 1):
        recentTag, tags = "", ""
    elif len(tags) == 1:
        recentTag, tags = tags[0], tags[0]
    else:
        recentTag, tags = tags[0], tags[1:]

    return (tags, recentTag)

# Sort tag names
def tagSortKey (tagName):
    m = re.search(r'\d+(\.\d+)+', tagName)
    if m:
        return map(int, m.group().split('.'))
    else:
        return [0,0,0,0]
