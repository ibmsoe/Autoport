def collapse_spaces(line):
    add = False
    l = ''

    for c in line:
        if c.isspace() and add:
            if c == '\n':
                l = l + '; '
            else:
                l = l + c
            add = False
        if not c == ' ':
            add = True
            l = l + c

    return l

def collapse_semicolons(line):
    add = False
    l = ''

    for c in line:
        if c == ';' and add:
            l = l + c
            add = False
        if not c == ';':
            add = True
            l = l + c

    return l

def clean(line):
    clean = collapse_spaces(line)
    
    if clean[0] == '$':
        clean = clean[1 : len(clean)]

    clean = collapse_semicolons(clean)
    clean = collapse_spaces(clean)
    
    return clean
