PYTHON=python3
FFMPEG=ffmpeg-git-amd64-static.tar.xz
LIBOPUS=opus-1.3.1.tar.gz
install:
	@echo installing requirements...
	@$(PYTHON) -m pip install -r requirements.txt
	@echo download and extracting dependencies...
ifeq ("$(wildcard ffmpeg)","")
ifeq ("$(wildcard $(FFMPEG))","")
	@curl https://johnvansickle.com/ffmpeg/builds/$(FFMPEG) -o $(FFMPEG)
endif
	@tar -xf $(FFMPEG)
	@mv $$(tar -xvf $(FFMPEG) | head -n 1)ffmpeg .
	@rm -rf $$(tar -xvf $(FFMPEG) | head -n 1) $(FFMPEG)
endif
ifeq ("$(wildcard libopus.so)","")
ifeq ("$(wildcard $(LIBOPUS))","")
	@curl https://archive.mozilla.org/pub/opus/$(LIBOPUS) -o $(LIBOPUS)
endif
	@tar -xf $(LIBOPUS)
	@cd $$(tar -xvf $(LIBOPUS) | head -n 1) && sh configure && make
	@cp $$(tar -xvf $(LIBOPUS) | head -n 1).libs/libopus.so .
	@rm -rf $$(tar -xvf $(LIBOPUS) | head -n 1) $(LIBOPUS)
endif
	@echo done
