#
# Makefile - build wrapper for awscli on CentPOS 7
#
#	git clone RHEL 7 SRPM building tools from
#	https://github.com/nkadel/[package] into designated
#	AWSCLIPKGS below
#
#	Set up local 

# Rely on local nginx service poingint to file://$(PWD)/epelrpmmacrorepo
#REPOBASE = http://localhost
REPOBASE = file://$(PWD)

#
AWSCLIPKGS+=python-rpmautospec-core-srpm
AWSCLIPKGS+=epel-rpm-macros-srpm
AWSCLIPKGS+=go-srpm-macros-epel-srpm
AWSCLIPKGS+=rpc-packaging-srpm
AWSCLIPKGS+=rust-packaging-srpm

REPOS+=epelrpmmacrorepo/el/10

REPODIRS := $(patsubst %,%/x86_64/repodata,$(REPOS)) $(patsubst %,%/SRPMS/repodata,$(REPOS))

# No local dependencies at build time
CFGS+=epelrpmmacrorepo-10-x86_64.cfg

# Link from /etc/mock
MOCKCFGS+=alma+epel-10-x86_64.cfg

all:: tpl
all:: install
install:: $(CFGS) $(MOCKCFGS)
install:: $(REPODIRS)
install:: $(EPELPKGS)
install:: $(AWSCLIPKGS)

build install clean getsrc build:: FORCE
	@for name in $(EPELPKGS) $(AWSCLIPKGS); do \
	     (cd $$name; $(MAKE) $(MFLAGS) $@); \
	done  

# It is sometimes useful to build up all the more independent EPEL packages first
epel:: $(EPELPKGS)

# Dependencies for order sensitivity
#python-awscli-srpm::

# Actually build in directories
$(EPELPKGS):: FORCE
	(cd $@; $(MAKE) $(MLAGS) install)

$(AWSCLIPKGS):: FORCE
	(cd $@; $(MAKE) $(MLAGS) install)

repos: $(REPOS) $(REPODIRS)
$(REPOS):
	install -d -m 755 $@

.PHONY: $(REPODIRS)
$(REPODIRS): $(REPOS)
	@install -d -m 755 `dirname $@`
	/usr/bin/createrepo_c `dirname $@`

.PHONY: cfg cfgs
cfg cfgs:: $(CFGS) $(MOCKCFGS)

$(MOCKCFGS)::
	@echo Generating $@ from /etc/mock/$@
	@echo "include('/etc/mock/$@')" | tee $@

epelrpmmacrorepo-10-x86_64.cfg: /etc/mock/alma+epel-10-x86_64.cfg
	@echo Generating $@ from $?
	@echo "include('$?')" | tee $@
	@echo | tee -a $@
	@echo "config_opts['root'] = 'epelrpmmacrorepo-{{ releasever }}-{{ target_arch }}'" | tee -a $@
	@echo "config_opts['yum.conf'] += \"\"\"" | tee -a $@
	@echo '[epelrpmmacrorepo]' | tee -a $@
	@echo 'name=epelrpmmacrorepo' | tee -a $@
	@echo 'enabled=1' | tee -a $@
	@echo 'baseurl=$(REPOBASE)/epelrpmmacrorepo/el/10/x86_64/' | tee -a $@
	@echo 'failovermethod=priority' | tee -a $@
	@echo 'skip_if_unavailable=False' | tee -a $@
	@echo 'metadata_expire=1' | tee -a $@
	@echo 'gpgcheck=0' | tee -a $@
	@echo '#cost=2000' | tee -a $@
	@echo '"""' | tee -a $@

repo: epelrpmmacrorepo.repo
epelrpmmacrorepo.repo:: Makefile epelrpmmacrorepo.repo.in
	if [ -s /etc/fedora-release ]; then \
		cat $@.in | \
			sed "s|@REPOBASEDIR@/|$(PWD)/|g" | \
			sed "s|/@RELEASEDIR@/|/fedora/|g" > $@; \
	elif [ -s /etc/redhat-release ]; then \
		cat $@.in | \
			sed "s|@REPOBASEDIR@/|$(PWD)/|g" | \
			sed "s|/@RELEASEDIR@/|/el/|g" > $@; \
	else \
		echo Error: unknown release, check /etc/*-release; \
		exit 1; \
	fi

tpl:: epel-10.tpl
.PHONY: epel-10.tpl
epel-10.tpl::
	@echo "config_opts['chroot_setup_cmd'] += \" epel-rpm-macros\"" | tee $@
	@echo "config_opts['dnf.conf'] += \"\"\"" | tee -a $@
	@echo '[epelrpmmacro]' | tee -a $@
	@echo 'name=EPEL RPM Macro repo' | tee -a $@
	@echo 'enabled=1' | tee -a $@
	@echo 'baseurl=$(REPOBASE)/epelrpmmacrorepo/el/8/x86_64/' | tee -a $@
	@echo 'failovermethod=priority' | tee -a $@
	@echo 'skip_if_unavailable=False' | tee -a $@
	@echo 'metadata_expire=1' | tee -a $@
	@echo 'gpgcheck=0' | tee -a $@
	@echo '#cost=2000' | tee -a $@
	@echo '"""' | tee -a $@

epel-10.tpl::
	cmp -s /etc/mock/templates/$@ $@

clean::
	find . -name \*~ -exec rm -f {} \;
	rm -f *.cfg
	rm -f *.out
	rm -f *.tpl
	@for name in $(AWSCLIPKGS); do \
	    $(MAKE) -C $$name clean; \
	done

distclean:
	rm -rf $(REPOS)

maintainer-clean:
	rm -rf $(AWSCLIPKGS)

FORCE::
