deploy:
	ssh hass "rm -rf /root/config/custom_components/myrt-desk"
	scp -r custom_components/myrt-desk hass:/root/config/custom_components/myrt-desk
restart:
	ssh hass "source /etc/profile.d/homeassistant.sh && ha core restart"
configure:
	python3 -m venv ./venv
	. venv/bin/activate; pip3 install -r requirements.txt
clean:
	rm -rf venv
lint:
	. venv/bin/activate; pylama custom_components/
