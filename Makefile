# requires:
# latex2html and pdflatex
# XML output of mif2xml-0.3 in SRC

MIFX:=$(PWD)/mifx2tex.py
DEST=tex
SRC=/home/jr76/mif/AppDevGuideMIF

TEXS = \
$(DEST)/titlepage.tex \
$(DEST)/introduction.tex \
$(DEST)/gettingStarted.tex \
$(DEST)/overview.tex \
$(DEST)/epicsBuildFacility.tex \
$(DEST)/lockScanProcess.tex \
$(DEST)/databaseDefinition.tex \
$(DEST)/iocInit.tex \
$(DEST)/accessSecurity.tex \
$(DEST)/test.tex \
$(DEST)/errorLogging.tex \
$(DEST)/recordSupport.tex \
$(DEST)/deviceSupport.tex \
$(DEST)/driverSupport.tex \
$(DEST)/staticDatabaseAccess.tex \
$(DEST)/runtimeDatabaseAccess.tex \
$(DEST)/generalPurposeTasks.tex \
$(DEST)/scanning.tex \
$(DEST)/iocsh.tex \
$(DEST)/libCom.tex \
$(DEST)/libComOsi.tex \
$(DEST)/registry.tex \
$(DEST)/databaseStructures.tex

all: AppDevGuide.pdf AppDevGuide

AppDevGuide.pdf: AppDevGuide.tex $(TEXS)
	./build_latex AppDevGuide

AppDevGuide: AppDevGuide.tex $(TEXS)
	latex2html $< -split +1

$(DEST)/%.tex: $(SRC)/%.mif.xml $(MIFX)
	mkdir -p $(DEST)
	$(MIFX) $< > $@

.PHONY: clean
clean:
	rm -rf AppDevGuide
	rm -f *.idx *.ind *.ilg *.log *.out *.pdf *.toc *.aux


