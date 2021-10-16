run: env_stamp
	. env/bin/activate; ./torrent-queuer

env_stamp:
	python3 -m venv env
	. env/bin/activate; pip install tpblite pylint
	touch $@

lint:
	. env/bin/activate; pylint *.py torrent-queuer
