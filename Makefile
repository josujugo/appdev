MIFX:=$(PWD)/mifx2tex.py
VPATH=AppDevGuideMIF
DEST=tex

TARGETS = \
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

all: $(DEST) $(TARGETS)
$(DEST):
	mkdir -p $@

$(DEST)/%.tex: %.mif.xml $(MIFX)
	$(MIFX) $< > $@
