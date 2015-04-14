# Let's put often used management commands in this Makefile so we can use it as
# executable documentation
TEST_COMMAND=manage.py test smeuhoverride


install:
	pip install -r requirements.txt
	python manage.py migrate


test:
	python $(TEST_COMMAND)

coverage:
	coverage run --source=. $(TEST_COMMAND)

fasttest:
	DJANGO_TEST_FAST=1 python manage.py test --failfast smeuhoverride threadedcomments


.PHONY: deploy
deploy:
	fab -R smeuh deploy

serve:
	python manage.py runserver

.PHONY: backup
backup:
	fab backup
