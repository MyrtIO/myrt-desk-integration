VENV_PATH = ./venv
VENV = . $(VENV_PATH)/bin/activate;
COMPONENT_NAME = myrt_desk
COMPONENT_PATH = home-assistant/custom_components/$(COMPONENT_NAME)

deploy:
	ssh home.local "sudo rm -rf $(COMPONENT_PATH)"
	rsync -r custom_components/$(COMPONENT_NAME)/ home.local:$(COMPONENT_PATH)
restart:
	ssh hass "source /etc/profile.d/homeassistant.sh && ha core restart"
configure:
	python3 -m venv $(VENV_PATH)
	$(VENV) pip install -r requirements.txt
clean:
	rm -rf venv
lint:
	$(VENV) pylint custom_components/
