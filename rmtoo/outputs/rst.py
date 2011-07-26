#
# rmtoo 
#   Free and Open Source Requirements Management Tool
#
# reStructuredText output class

import os
import time

from rmtoo.lib.TopicSet import TopicSet
from rmtoo.lib.Constraints import Constraints
from rmtoo.lib.RMTException import RMTException

class rst:
    default_config = { "req_attributes":
                       ["Priority", "Owner", "Invented on",
                        "Invented by", "Status", "Class"] }

    level_names = '=-*^~#'

    def __init__(self, params):
        self.topic_name = params[0]
        self.filename = params[1]
        self.config = rst.default_config
        if len(params)>2:
            self.config = params[2]

    def set_topics(self, topics):
        self.topic_set = topics.get(self.topic_name)

    @staticmethod
    def strescape(string):
        return string
        #r = []
        #for s in string:
            #if s in '_/':
                #r.append('--')
            #elif ord(s)>=32 and ord(s)<127:
                #r.append(s)
            #else:
                #r.append("%02x" % ord(s))
        #return ''.join(r)

    # Create Makefile Dependencies
    def cmad(self, reqscont, ofile):
        ofile.write("REQS_RST=%s\n" % self.filename)
        reqset = reqscont.continuum_latest()
        # For each requirement get the dependency correct
        ofile.write("%s: " % self.filename)
        for r in reqset.reqs:
            ofile.write("%s/%s.req "
                        % (reqscont.config.reqs_spec["directory"],
                           reqset.reqs[r].id))
        ofile.write("\n\t${CALL_RMTOO}\n")

    # The real output
    # Note that currently the 'reqscont' is not used in case of topics
    # based output.
    def output(self, reqscont):
        # Currently just pass this to the RequirementSet
        self.output_reqset(reqscont.continuum_latest())

    def output_reqset(self, reqset):
        # Call the topic to write out everything
        self.output_rst_topic_set(self.topic_set, reqset.ce3set)

    def output_rst_topic_set(self, topic_set, ce3set):
        fd = file(self.filename, "w")
        # The TopicSet itself needs no output.
        self.output_rst_topic(fd, topic_set.get_master(), ce3set)
        constraints = Constraints.collect(topic_set)
        self.output_rst_constraints(fd, topic_set, constraints)
        fd.close()

    def output_rst_topic(self, fd, topic, ce3set):
        fd.write("\n..  Output topic '%s'\n\n" % topic.name)
        for t in topic.t:

            tag = t.get_tag()
            val = t.get_content()

            if tag == "Name":
                # The name itself is dependent on the level
                fd.write(val)
                fd.write("\n")
                fd.write(self.level_names[topic.level] * len(val))
                fd.write("\n\n")
                continue

            if tag == "SubTopic":
                rtopic = topic.find_outgoing(val)
                self.output_rst_topic(fd, rtopic, ce3set)
                continue

            if tag == "Text":
                fd.write("%s\n" % val)
                continue

            if tag == "IncludeRequirements":
                self.output_requirements(fd, topic, ce3set)
                continue

            raise RMTException(84, "Unknown tag '%s' in "
                  "topic file" % tag)

    def output_requirements(self, fd, topic, ce3set):
        for req in sorted(topic.reqs, key = lambda r: r.id):
            self.output_requirement(fd, req, topic.level + 1, ce3set)

    def output_requirement(self, fd, req, level, ce3set):
        fd.write("\n..  REQ '%s'\n\n" % req.id)

        name = req.get_value("Name").get_content()
        label = rst.strescape(req.id)
        description = req.get_value("Description").get_content()
        fd.write('.. _%s:\n\n'%label)
        fd.write(name + '\n')
        fd.write((self.level_names[level] * len(name)) + '\n\n')
        fd.write('*Description:* ' + description + '\n')

        if req.is_val_av_and_not_null("Rationale"):
            fd.write('\n*Rationale:* %s\n'%req.get_value(
                "Rationale").get_content())

        if req.is_val_av_and_not_null("Note"):
            fd.write('\n*Note:* %s\n'%req.get_value(
                "Note").get_content())

        # Only output the depends on when there are fields for output.
        if len(req.outgoing)>0:
            # Create links to the corresponding labels.
            fd.write('\n*Depends on:* \n\n')
            for d in req.outgoing:
                fd.write('+ :ref:`%s`\n'%rst.strescape(d.id))

        if len(req.incoming)>0:
            # Create links to the corresponding dependency nodes.
            fd.write('\n*Solved by:* \n\n')
            for d in sorted(req.incoming, key=lambda r: r.id):
                fd.write('+ :ref:`%s`\n'%rst.strescape(d.id))


        cnstrt = ce3set.get(req.get_id())
        if cnstrt!=None and cnstrt.len()>0:
        #if req.is_val_av_and_not_null("Constraints"):
            fd.write('\n*Constraints:* \n\n')
            for k, v in sorted(cnstrt.get_values().iteritems()):
                refid = rst.strescape(k)
                fd.write('+ :ref:`CONSTRAINT%s`'%refid)
                description = v.description()
                if description!=None:
                    fd.write(' [' + description + ']')
                fd.write('\n')

        status = req.get_value("Status").get_output_string()
        clstr = req.get_value("Class").get_output_string()

        fd.write('\n*Id:* ``%s``\n'%(req.id))

        # Put mostly three things in a line.

        class Table:

            def __init__(self):
                self.rattrs = []
                self.max_length = 0

            def append(self, attribute, value):
                self.max_length = max(
                        self.max_length, len(attribute), len(value))
                self.rattrs.append(attribute)
                self.rattrs.append(value)

            def as_string(self):
                separator = (
                        '+' +
                        '+'.join(['-' * (self.max_length + 2)] * 6)+
                        '+\n')
                cell = '%%-%ds'%self.max_length
                a = self.rattrs[:]
                a += [''] * ((-len(a)) % 6)
                a = [cell%i for i in a]
                lines = []
                for i in range(0, len(a), 6):
                    lines.append(
                            '| ' +
                            ' | '.join(a[i:i+6]) +
                            ' |\n')
                return (separator +
                        separator.join(lines) +
                        separator)

        t = Table()

        for rattr in self.config['req_attributes']:
            if rattr=="Priority":
                t.append(
                        '*Priority*:',
                        '%4.2f'%(req.get_value('Priority') * 10))
            elif rattr=="Owner":
                t.append('*Owner*:', req.get_value('Owner'))
            elif rattr=="Invented on":
                t.append(
                        '*Invented on:*',
                        req.get_value("Invented on").strftime("%Y-%m-%d"))
            elif rattr=="Invented by":
                t.append('*Invented by:*', req.get_value("Invented by"))
            elif rattr=="Status":
                t.append('*Status:*', status)
            elif rattr=="Class":
                t.append('*Class:*', clstr)
            else:
                # This only happens when a wrong configuration is supllied.
                raise RMTException(85, "Wrong latex2 output configuration "
                                   "supplied: unknown tag [%s]" % rattr)
        fd.write('\n')
        fd.write(t.as_string())

    def output_rst_constraints(self, fd, topic_set, constraints):

        #print("AC %s" % self.constraints)

        if len(constraints)>0:
            fd.write("Constraints\n")
            fd.write((self.level_names[0] * 11) + "\n")
            for cname, cnstrt in sorted(constraints.iteritems()):
                self.output_rst_one_constraint(fd, cname, cnstrt)

    def output_rst_one_constraint(self, fd, cname, cnstrt):
        cname = rst.strescape(cname)
        fd.write("\n..  CONSTRAINT '%s'\n\n" % cname)

        name = cnstrt.get_value("Name").get_content()
        description = cnstrt.get_value("Description").get_content()
        fd.write('.. _CONSTRAINT%s:\n\n'%(cname))
        fd.write(name + '\n')
        fd.write((self.level_names[1] * len(name)) + '\n\n')
        fd.write('*Description:* ' + description + '\n')

        if cnstrt.is_val_av_and_not_null("Rationale"):
            fd.write('\n*Rationale:* %s\n'
                     % cnstrt.get_value("Rationale").get_content())

        if cnstrt.is_val_av_and_not_null("Note"):
            fd.write('\n*Note:* %s\n'
                     % cnstrt.get_value("Note").get_content())
