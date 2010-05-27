# requires:
# latex2html and pdflatex
# XML output of mif2xml-0.3 in SRC

MIFX:=$(PWD)/mifx2tex.py
DEST=tex
SRC=/home/jr76/mif/AppDevGuideMIF
PDFD=pdf
EPSD=eps

PDFS = \
$(PDFD)/overview_1.pdf \
$(PDFD)/overview_6.pdf \
$(PDFD)/accessSecurity_1.pdf \
$(PDFD)/lockScanProcess_26.pdf  \
$(PDFD)/lockScanProcess_6.pdf  \
$(PDFD)/lockScanProcess_34.pdf \
$(PDFD)/lockScanProcess_9.pdf \
$(PDFD)/lockScanProcess_16.pdf \
$(PDFD)/lockScanProcess_37.pdf \
$(PDFD)/lockScanProcess_1.pdf \
$(PDFD)/lockScanProcess_40.pdf \
$(PDFD)/scanning_1.pdf \
$(PDFD)/scanning_12.pdf \
$(PDFD)/scanning_19.pdf \
$(PDFD)/databaseStructures_1.pdf

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

AppDevGuide.pdf: AppDevGuide.tex $(TEXS) $(PDFS)
	./build_latex AppDevGuide

AppDevGuide: AppDevGuide.tex $(TEXS)
	latex2html $< -split +1

$(PDFD)/%.pdf: $(EPSD)/%.eps
	mkdir -p $(PDFD)
	epstopdf $< -o=$@

$(DEST)/%.tex: $(SRC)/%.mif.xml $(MIFX)
	mkdir -p $(DEST)
	$(MIFX) $< > $@

.PHONY: clean
clean:
	rm -rf AppDevGuide
	rm -rf pdf
	rm -f *.idx *.ind *.ilg *.log *.out *.pdf *.toc *.aux

