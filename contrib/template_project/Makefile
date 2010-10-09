.PHONY: all
.PHONY: all_html
all: latex/requirements.pdf artifacts/req-graph1.png \
	artifacts/req-graph2.png all_html


# Adding new files (especially requirements) can not automatically
# handled.  The 'force' target tries to handle this.
.PHONY: force
force: 
	rm .rmtoo_dependencies
	${MAKE} all

#
# This is the way the rmtoo must be called.
# (The variable is set in the setenv.sh script)
#
CALL_RMTOO=${RMTOO_CALL} -f Config.py

#
# Dependency handling
#  The file .rmtoo_dependencies is created by rmtoo itself.
#
include .rmtoo_dependencies

all_html: ${OUTPUT_HTML}

# And how to make the dependencies
.rmtoo_dependencies:
	${CALL_RMTOO} \
		--create-makefile-dependencies=.rmtoo_dependencies

artifacts/req-graph1.png: artifacts/req-graph1.dot
	unflatten -l 23 artifacts/req-graph1.dot | \
		dot -Tpng -o artifacts/req-graph1.png

artifacts/req-graph2.png: artifacts/req-graph2.dot
	dot -Tpng -o artifacts/req-graph2.png artifacts/req-graph2.dot

# Two calls are needed: one for the requirments converting and one for
# backlog creation.
latex/requirements.pdf: ${REQS_LATEX2} latex/requirements.tex
	(cd artifacts && \
	   gnuplot ${RMTOO_CONTRIB_DIR}/contrib/gnuplot_stats_reqs_cnt.inc && \
	   epstopdf stats_reqs_cnt.eps)
	(cd latex && pdflatex requirements.tex; \
		pdflatex requirements.tex; \
		pdflatex requirements.tex)

.PHONY: clean
clean:
	rm -fr artifacts/html
	rm -f artifacts/* \
		latex/requirements.aux latex/requirements.dvi \
		latex/requirements.log latex/requirements.out \
		latex/requirements.pdf latex/requirements.toc \
		add_data.py*
	rm -fr debian/rmtoo build