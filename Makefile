REQUIREMENTS = requirements.txt
LAYER_DIR = layers/scraping_layer/python

build-layer:
	@echo "Cleaning old layer files..."
	rm -rf $(LAYER_DIR)
	@echo "Downloading dependencies for Lambda layer..."
	pip install -r $(REQUIREMENTS) -t $(LAYER_DIR) --platform manylinux2014_x86_64 --only-binary=:all: --python-version 3.13
	@echo "Done! Layer dependencies are ready for Terraform."

clean:
	@echo "Cleaning temporary layer files..."
	rm -rf $(LAYER_DIR)
	@echo "Cleaned successfully."

help:
	@echo "Usage:"
	@echo "  make build-layer  - Download Linux-compatible libraries for Terraform"
	@echo "  make clean        - Remove downloaded libraries"