# Let's put often used management commands in this Makefile so we can use it as
# executable documentation
install:
	pip install -r requirements.txt
	python manage.py syncdb


test:
	python manage.py test smeuhoverride

fasttest:
	DJANGO_TEST_FAST=1 python manage.py test --failfast smeuhoverride


.PHONY: deploy
deploy:
	fab -R smeuh deploy

serve:
	python manage.py runserver
