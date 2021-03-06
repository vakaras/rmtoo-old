#
# -*- coding: utf-8 -*-
#
# Analytics: Description Words
#
#  The Description is the critical part of the requirement. This
#  module checks for some good and bad words and tries a heuristic to
#  get an idea about bad requirement descriptions.
#
# (c) 2010 by flonatel
#
# For licencing details see COPYING
#

import re

from rmtoo.lib.LaTeXMarkup import LaTeXMarkup

class DescWords:

    # This is the assesment of each word (better regular expression).
    # If the regular expression matches, the value is added.
    # If the resulting number is lower than a given limit, an error is
    # assumed. 
    # The numbers are provided on a level between [-100, 100] where
    # -100 is a very very bad word and 100 is a very very good.
    # Do not add the single word 'not': only do this in pairs,
    # e.g. 'must not'.
    words_en_GB = [
        [ re.compile("\. "), -15, "Additional fullstop (not only at the end of the desctiption)"],
        [ re.compile(" about "), -15, "Usage of the word 'about'"],
        [ re.compile(" and "), -10, "Usage of the word 'and'"],
        [ re.compile(" approximately "), -100, "Usage of the word 'approximately'"],
        [ re.compile(" etc\.? "), -40, "Usage of the word 'etc'"],
        [ re.compile(" e\.g\. "), -40, "Usage of the word 'e.g.'"],
        [ re.compile(" has to "), 20, "Usage of the word 'has to'"],
        [ re.compile(" have to "), 20, "Usage of the word 'have to'"],
        [ re.compile(" i\.e\. "), -40, "Usage of the word 'i.e.'"],
        [ re.compile(" many "), -20, "Usage of the word 'many'"],
        [ re.compile(" may "), 10, "Usage of the word 'may'"],
        [ re.compile(" maybe "), -50, "Usage of the word 'maybe'"],
        [ re.compile(" might "), 10, "Usage of the word 'might'"],
        [ re.compile(" must "),  25, "Usage of the word 'must'"],
        [ re.compile(" or "), -15, "Usage of the word 'or'"],
        [ re.compile(" perhaps "), -100, "Usage of the word 'perhaps'"],
        [ re.compile(" should "), 15, "Usage of the word 'should'"],
        [ re.compile(" shall "), 15, "Usage of the word 'shall'"],
        [ re.compile(" some "), -25, "Usage of the word 'some'"],
        [ re.compile(" vaguely "), -25, "Usage of the word 'vaguely'"],
    ]

    words_de_DE = [
        [ re.compile("\. "), -15, "Additional fullstop (not only at the end of the desctiption)"],
        [ re.compile(" ca\. "), -75, "Usage of the word 'ca.'"],
        [ re.compile(" möglicherweise "), -100, "Usage of the word 'möglicherweise'"],
        [ re.compile(" muss "), 25, "Usage of the word 'muss'"],
        [ re.compile(" oder "), -15, "Usage of the word 'oder'"],
        [ re.compile(" und "), -10, "Usage of the word 'und'"],
        [ re.compile(" usw."), -40, "Usage of the word 'usw'"],
        [ re.compile(" vielleicht "), -25, "Usage of the word 'vielleicht'"],
        [ re.compile(" z\.B\. "), -40, "Usage of the word 'z.B.'"],
    ]

    words = { "en_GB": words_en_GB,
              "de_DE": words_de_DE, }

    @staticmethod
    def get_lang(config):
        if "default_language" in config.reqs_spec:
            if config.reqs_spec["default_language"] in DescWords.words:
                return DescWords.words[config.reqs_spec["default_language"]]
            else:
                return None
        return DescWords.words["en_GB"]

    @staticmethod
    def analyse(lwords, text):
        # Must be at least some positive things to get this
        # positive. (An empty description is a bad one.)
        level = -10
        log = []
        for wre, wlvl, wdsc in lwords:
            plain_txt = LaTeXMarkup.replace_txt(text).strip()
            fal = len(wre.findall(plain_txt))
            if fal>0:
                level += fal*wlvl
                log.append("%+4d:%d*%d: %s" % (fal*wlvl, fal, wlvl, wdsc))
                # Note the result of this test in the requirement itself.
        return [level, log]

    @staticmethod
    def run(config, reqs, topics):
        # Try to get the correct language
        lwords = DescWords.get_lang(config)
        # If language is not available, this analytics make no sense.
        if lwords==None:
            return True

        ok = True
        for req in sorted(reqs.reqs.values(), key=lambda r: r.id):
            ares = DescWords.analyse(
                lwords, req.get_value("Description").get_content())
            req.analytics["DescWords"] = ares
            if ares[0]<0:
                ok = False
            
        return ok
