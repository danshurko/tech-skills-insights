LAYER_ZIP=layer.zip
REQUIREMENTS=requirements.txt

layer:
	rm -rf python $(LAYER_ZIP)
	mkdir -p python
	pip install -r $(REQUIREMENTS) -t python/
	zip -r $(LAYER_ZIP) python
	rm -rf python
	@echo "Created $(LAYER_ZIP)"

clean:
	rm -rf python $(LAYER_ZIP)
	@echo "Cleaned temporary files"

help:
	@echo "Usage:"
	@echo "  make layer  - build layer.zip with libraries"
	@echo "  make clean  - clean all temporary files"
