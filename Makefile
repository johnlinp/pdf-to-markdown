all:
	@echo 'please run "make publish" to publish'

publish:
	python2 setup.py sdist bdist_wheel
	twine upload dist/*

clean:
	rm -rf build dist *.egg-info
