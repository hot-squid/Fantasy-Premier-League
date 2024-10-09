def drop_keys(d, keys):
    '''Used to drop an array of keys from a dictionary'''
    return {k: v for k, v in d.items() if k not in keys}
