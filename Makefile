PWD=$(shell pwd)
-include $(SDK_CONFIG_CONFIG)

MY_NAME = tradeP9

#** include *.mk **
-include define.mk

#[major].[minor].[revision].[build]
VERSION_MAJOR = 1
VERSION_MINOR = 0
VERSION_REVISION = 0
VERSION_FULL = $(VERSION_MAJOR).$(VERSION_MINOR).$(VERSION_REVISION)
LIBNAME_A = xxx
LIBNAME_SO =
LIBNAME_MOD =

#** GITHUB_LIBS **
GITHUB_LIBS = \
#														https://github.com/lankahsu520/pythonP9.git

#** PYTHON_FILES **
PYTHON_FILES = \
														fubonp9_123 \
														esunp9_123 \
														backtesting_123

DEBUG=3
DEBUG_ARG=-d $(DEBUG)

export PJ_PYTHON_VER=$(shell python -c 'import sys; print("{0[0]}.{0[1]}".format(sys.version_info))')
export MAKE_DBG='==\> python $(PJ_PYTHON_VER) -'

#********************************************************************************
#** All **
#********************************************************************************

.DEFAULT_GOAL = all

.PHONY: all clean distclean layer_python
all: $(PYTHON_FILES)

clean:
	$(PJ_SH_RM) export.log .layer_python
	$(PJ_SH_RM) .configured
	$(PJ_SH_RMDIR) __pycache__/ $(MY_NAME)/__pycache__/ log/ ./python/ github_libs/
	$(PJ_SH_RM) $(MY_NAME)/version.txt
	@for subdir in $(CONFS_yes); do \
		[ -d "$$subdir" ] && (make -C $$subdir $@;) || echo "skip !!! ($$subdir)"; \
	done

distclean: clean

.layer_python:
	#@echo '$(MAKE_DBG) $@: $(PWD)/python'
	#@if [ ! -d "$(PWD)/python" ]; then \
	#	(pip3 install --upgrade --force-reinstall --target $(PWD)/python -r $(MY_NAME)/requirements.txt); \
	#	for libs in $(GITHUB_LIBS); do (git clone $$libs github_libs && $(PJ_SH_CP) github_libs/*.py $(PWD)/python && rm -rf github_libs); done \
	#fi
	@echo '----->> $@ - pip install -r $(MY_NAME)/requirements.txt'
	(pip install -r $(MY_NAME)/requirements.txt)
	@echo
	touch $@

$(PYTHON_FILES): .layer_python
	@echo
	@echo '$(MAKE_DBG) run: $@'
	#PYTHONPATH=$(PWD)/python python -m $(MY_NAME).$@ $(DEBUG_ARG)
	./$@.py $(DEBUG_ARG)
