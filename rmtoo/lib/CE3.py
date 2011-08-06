#
# rmtoo
#   Free and Open Source Requirements Management Tool
#
# Constraint Execution and Evaluation Environment
#
# (c) 2011 by flonatel
#
# For licencing details see COPYING
#

from rmtoo.lib.RMTException import RMTException

# Some common used functions
def ce3assert(b, errmsg):
    if not b:
        raise RMTException(90, "Failed CE3 assert: msg [%s]"
                           % errmsg)

class CE3:

    def __init__(self):
        self.values = {}

    def eval(self, cs, class_name, cstr_call):
        v = cs.get_value("CE3")

        if v==None:
            return

        s = ""
        for r in v.get_content_with_nl():
            s += r[1:] + "\n"

        exec(s) in globals(), locals()
        exec("self.values[class_name] = %s" % cstr_call)

    def has_key(self, k):
        return k in self.values

    def get_keys(self):
        return self.values.keys()

    def get_value(self, k):
        return self.values[k]

    def set_value(self, k, v):
        self.values[k] = v

    def get_values(self):
        return self.values

    def len(self):
        return len(self.values)

    # Try to unite all given ce3s into the local ce3
    def unite(self, oce3s):
        okeys = set()
        for o in oce3s:
            okeys = okeys.union(set(o.get_keys()))
 
        for k in okeys:
            # Is the key locally available?
            mobj = None
            if self.has_key(k):
                mobj = self.get_value(k)

            lobj = []
            # Look for this in all other oce3s
            for o in oce3s:
                if o.has_key(k):
                    lobj.append(o.get_value(k))
            
            # For the execution one object is needed
            eobj = mobj
            if mobj==None:
                eobj = lobj[0]
                ### lobj.add(eobj)

            ro = eobj.unite(mobj, lobj)

            if ro!=None:
                # There is a new constraint for the local key
                assert(mobj==None)
                self.set_value(k, ro)

                
