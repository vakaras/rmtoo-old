#
# rmtoo
#   Free and Open Source Requirements Management Tool
#
# RequirementSet
#
# (c) 2010-2011 by flonatel
#
# For licencing details see COPYING
#

import os
import re
import sys
import time
import codecs
import operator
import StringIO

from rmtoo.lib.Requirement import Requirement
from rmtoo.lib.Constraint import Constraint
from rmtoo.lib.digraph.Digraph import Digraph
from rmtoo.lib.MemLogStore import MemLogStore
from rmtoo.lib.storagebackend.RecordEntry import RecordEntry

# This class handles a whole set of requirments.
# These set must be enclosed, i.e. all references must be resolvable.

class RequirementSet(Digraph, MemLogStore):

    er_fine = 0
    er_error = 1

    def __init__(self, mods, opts, config):
        Digraph.__init__(self)
        MemLogStore.__init__(self)
        self.reqs = {}
        self.mods = mods
        self.opts = opts
        # The requirement set is only (fully) usable, when everything
        # is fine.
        self.state = self.er_fine
        self.config = config
        self.version_id = None

        # The analytic modules store the results in this map:
        self.analytics = {}
        self.constraints = {}

    def handle_modules(self):
        # Dependencies can be done, if all requirements are successfully
        # read in.
        self.handle_modules_reqdeps()
        # If there was an error, the state flag is set:
        if self.state != self.er_fine:
            self.error(43, "there was a problem handling the "
                       "requirement set modules")
            return False

        # The must no be left
        if not self.check_left_tags():
            self.error(56, "There were errors encountered during parsing "
                       "and checking - can't continue")
            return False

        return True

    # Read the whole requirement set from files stored in the
    # filesystem (which is typically the latest version when a repo is
    # available). 
    def read_from_filesystem(self, directory):
        everythings_fine = self.read(directory)
        if not everythings_fine:
            self.error(44, "There were errors in the requirment set")
            self.state = self.er_error
            return False

        everythings_fine = self.read_constraints(
            self.config.constraints_specs["search_dirs"])
        if not everythings_fine:
            self.error(86, "There were errors in the requirment set - "
                       "in the constraints")
            self.state = self.er_error
            return False

        return self.handle_modules()

    # Add requirement: this is needed when reading from VCS.
    def add_req(self, req):
        # Store in the map, so that it is easy to access the
        # node by id.
        self.reqs[req.id] = req
        # Also store it in the digraph's node list for simple
        # access to the digraph algorithms.
        self.nodes.append(req)

    def read(self, directory):
        everythings_fine = True
        for (path, dirs, files) in os.walk(directory):
            prefix = path[len(directory) + 1:]
            for f in files:
                m = re.match("^.*\.req$", f)
                if m==None:
                    continue
                rid = os.path.join(prefix, f[:-4])
                fd = codecs.open(os.path.join(path, f), "r", "utf-8")
                req = Requirement(
                        fd, rid, self, self.mods, self.opts, self.config)
                if req.ok():
                    # Store in the map, so that it is easy to access the
                    # node by id.
                    self.reqs[req.id] = req
                    # Also store it in the digraph's node list for simple
                    # access to the digraph algorithms.
                    self.nodes.append(req)
                else:
                    self.error(45, "could not be parsed", req.id)
                    everythings_fine = False
        self.ts = time.time()
        return everythings_fine

    # This is mostly a copy of the read - but changed at at least some
    # major points. 
    def read_constraints(self, directories):
        everythings_fine = True
        for da in directories:
            d = unicode(da, "utf-8")
            if not os.path.isdir(d):
                print("+++ WARN: skipping non-existant constraint "
                      "directory [%s]" % d)
                continue
            ef = self.read_constraints_one_dir(d)
            if not ef:
                everythings_fine = False
        return everythings_fine

    def read_constraints_one_dir(self, directory):
        everythings_fine = True
        files = os.listdir(directory)
        for f in files:
            m = re.match("^.*\.ctr$", f)
            if m==None:
                continue
            rid = f[:-4]
            fd = codecs.open(os.path.join(directory, f), "r", "utf-8")
            cnstrnt = Constraint(fd, rid, self, self.mods, 
                                 self.opts, self.config)
            if cnstrnt.ok():
                # Store in the map, so that it is easy to access the
                # node by id.
                self.constraints[cnstrnt.get_id()] = cnstrnt
            else:
                self.error(87, "could not be parsed", cnstrnt.get_id())
                everythings_fine = False
        self.ts = time.time()
        return everythings_fine

    # This is mostly the same functionallaty of similar method of the
    # class Requirement - but with one major difference: for this
    # implementation stop if an error occured.
    def handle_modules_reqdeps(self):
        for module in self.mods.reqdeps_sorted:
            state = module.rewrite(self)
            if state==False:
                # Some sematic error occured.
                self.state = self.er_error
                # Do not continue - return immediately, because some
                # algorithms rely on the correct run from others.
                return

    def check_left_tags(self):
        alls_fine = True
        for r in self.reqs:
            rr = self.reqs[r]
            if len(rr.brmo)>0:
                self.error(57, "No tag handler found for tag(s) '%s' "
                           "- Hint: typo in tag(s)?" % rr.brmo.keys(), rr.id)
                alls_fine = False
        return alls_fine

    # Return the timestamp of the whole Requirment Set.
    # This is the current time for FILES and the checkin point of time
    # for files from the repo.
    def timestamp(self):
        return self.ts

    # Return the number of requirments in this RequirementSet.  This
    # is e.g. needed for statistics.
    def reqs_count(self):
        return len(self.reqs)

    def not_usable(self):
        self.state = self.er_error

    def is_usable(self):
        return self.state == self.er_fine
        
    def set_version_id(self, vid):
        self.version_id = vid

    def own_write_analytics_result(self, mstderr):
        for k, v in sorted(self.analytics.items(),
                           key=operator.itemgetter(0)):
            if v[0]<0:
                mstderr.write("+++ Error:Analytics:%s:result is '%+3d'\n"
                              % (k, v[0]))
                for l in v[1]:
                    mstderr.write("+++ Error:Analytics:%s:%s\n" % (k, l))

    # Write out the analytics results.
    def write_analytics_result(self, mstderr):
        self.own_write_analytics_result(mstderr)
        for req in sorted(self.reqs.values(), key=lambda r: r.id):
            req.write_analytics_result(mstderr)

    def normalize_dependencies(self):
        for r in self.reqs.itervalues():
            # Remove the old 'Depends on'
            r.record.remove("Depends on")

            # Create the list of dependencies
            onodes = []
            for n in r.incoming:
                onodes.append(n.name)
            
            # If the onodes is empty: There must no old 'Solved by'
            # tag available - if so something completey strange has
            # happens and it is better to stop directly.
            if len(onodes)==0:
                assert(not r.record.is_tag_available("Solved by"))
                # Looks that everything is ok: continue
                continue

            onodes.sort()
            on = " ".join(onodes)

            # Check if there is already a 'Solved by'
            try:
                r.record.set_content("Solved by", on)
            except ValueError, ve:
                r.record.append(RecordEntry(
                        "Solved by", on,
                        "Added by rmtoo-normalize-dependencies"))
        return True

    def write_to_filesystem(self, directory):
        for r in self.reqs.itervalues():
            fd = file(directory + "/" + r.id + ".req", "w")
            r.record.write_fd(fd)
            fd.close()
        return True

# Not used at the moment
#    def edge_count(self):
#        r = 0
#        for n in self.reqs.itervalues():
#            r += len(n.outgoing)
#        return r

