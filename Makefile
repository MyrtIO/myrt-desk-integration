VENV_PATH = ./venv
VENV = . $(VENV_PATH)/bin/activate;
COMPONENT_NAME = myrt_desk

deploy:
	ssh hass "rm -rf config/custom_components/$(COMPONENT_NAME)"
	rsync -r custom_components/$(COMPONENT_NAME)/ hass:config/custom_components/$(COMPONENT_NAME)
restart:
	ssh hass "source /etc/profile.d/homeassistant.sh && ha core restart"
configure:
	python3 -m venv $(VENV_PATH)
	$(VENV) pip install -r requirements.txt
clean:
	rm -rf venv
lint:
	$(VENV) pylint custom_components/
