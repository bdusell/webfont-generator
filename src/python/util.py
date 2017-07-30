def indent(s, tab):
    return '\n'.join(tab + line for line in s.split('\n'))

def remove_suffix(s, suffix):
    was_there = s.endswith(suffix)
    if was_there:
        s = s[:-len(suffix)]
    return s, was_there
