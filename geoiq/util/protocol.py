import urllib
__all__ = ["obj_to_railsparams", "urlencode_params", "urlencode_dictvals"]

def urlencode_params(ps):
    if (dictlike(ps)): ps = ps.iteritems()
    
    return urllib.urlencode([ (k,v) for (k,v) in ps if v is not None ])

def urlencode_dictvals(d):
    assert(dictlike(d))
    return dict( (k, urllib.quote(str(v))) for (k,v) in d.iteritems() )

def obj_to_railsparams(obj, key_prefix="", first=True):
    """\
    Convert nested dict/list-alikes with simple values (a la JSON) into a
    iterator of key-value pairs that can be urlencoded into a rails-style
    set of post arguments.

    XREF: https://github.com/rack/rack/blob/master/lib/rack/utils.rb#L69
    
    Could be avoided by using the right content-type for JSON & json-encoding 
    the dict (I think rails will just do the right thing), but we can't do
    that for file uploads, which force us to use multipart/form-data.
 
    This will work even then (modulo limitations).
    
    Output is a list of tuples, not a dict, becuase order is really important:
    Arrays implicitly begin a new member when
     (a) their RHS is a simple value and the key is repeated.
     (b) they're a hash and a key is repeated from the previous entry.
 
    There's a bunch of hidden/undoc limitations.
      (See check_an_obj_to_railsparams for some assertions)

    Other limitations vs JSON:
      Empty dicts or arrays will be omitted, as will None values.
      All values are sent as strings.

    """

    # important to convert to a list, as it will be iter'ed over many times
    fin_obj = strip_empty_vals(obj)
    return list(obj_to_railsparams_imp(fin_obj, key_prefix, first, None))


def obj_to_railsparams_imp(obj, key_prefix="", first=True, common_key = None):
    if (first):
        check_can_obj_to_railsparams(obj)

    if dictlike(obj) and len(obj) > 0:
        if (common_key is not None):
            new_key = "%s[%s]" % (key_prefix, common_key)
            yield (new_key,obj[common_key])

        for (k,v) in obj.iteritems():
            # already sent common key:
            if common_key is not None and k == common_key: continue

            if first: new_key = "%s%s" % (key_prefix, k)
            else: new_key = "%s[%s]" % (key_prefix, k)
            subs = obj_to_railsparams_imp(v, key_prefix=new_key, first=False)
            for r in subs: yield r
    elif listlike(obj):
        for (i,v) in enumerate(obj):
            new_key = "%s[]" % key_prefix
            has_dicts, first_dict_key = get_common_dict_key(obj)
            
            subs = obj_to_railsparams_imp(v, key_prefix=new_key, 
                                      first=False,
                                      common_key=first_dict_key)
            for r in subs: yield r
    else:
        if obj is not None: yield (key_prefix, obj)

def dictlike(obj):
    return hasattr(obj, "iteritems")

def listlike(obj):
    return (not dictlike(obj) 
            and hasattr(obj, "__len__") 
            and hasattr(obj, "__iter__"))

def strip_empty_vals(obj):
    if (dictlike(obj)):
        if (len(obj) == 0): return None
        r = []
        for (k,v) in obj.iteritems():
            nv = strip_empty_vals(v)
            if nv is not None: r.append( (k,nv) )            
        return dict(r)

    elif(listlike(obj)):
        if (len(obj) == 0): return None
        r = []
        for v in obj:
            nv = strip_empty_vals(v)
            if nv is not None: r.append(nv)
        return r
    else:
        return obj

# Known limitations of the objs we can handle this way:
#  a) no nested arrays. 
#
#  b) all dict children of an array must have the same key.
def check_can_obj_to_railsparams(obj, parent_is_array = False):
    if listlike(obj): # It's a list!

        if (parent_is_array): 
            raise ValueError("System limitation: Cannot nest arrays")

        # Make sure all dict children have the same key:
        try:
            child_dicts, common_key = get_common_dict_key(obj)
        except KeyError:
            raise ValueError("System limitation: If an array contains dicts," +
                             " all children must have at least one key in" +
                             " common.")
        for v in obj: check_can_obj_to_railsparams(v, True)
    elif dictlike(obj):
        for (k,v) in obj.iteritems():
            if (k.find("[") >= 0 or 
                k.find("]") >= 0):
                raise ValueError("System limitation: Brackets disallowed in"+
                                 " keys")
            check_can_obj_to_railsparams(v, False)
    else:
        # TODO: not sure the following is the right stuff to check:
        if (obj is not None): # Let 'None' through:
            if hasattr(obj, 'read'):
                # File-like objects get special dispensation (they get
                #  picked up for multipart encoding).
                pass

            # Otherwise, make sure it has a "nice" str rep:
            elif ((not hasattr(obj, "__str__"))
                or (obj.__str__.__objclass__ is object) ):
                    raise ValueError("%s is not a simple value, or cannot be" +
                                     " converted into one via str(). Consider"+
                                     " implementing __str__?" % (str(obj)))

# Find a key that's common to all dicts, skipping non-dicts and empty dicts.
def get_common_dict_key(dicts):
    keyset = None
    for d in dicts:
        if dictlike(d):
            keys = set( k for (k,v) in d.iteritems() )
            if len(keys) > 0:
                if (keyset is None): keyset = keys
                else : keyset = keyset.intersection(keys)
    
    if (keyset is not None):
        return (True, keyset.pop())
    else: # no child dictionaries, or all child dicts were empty.
        return (False, None)
