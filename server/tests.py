# Uncomment if you want to run tests in transaction mode with a final rollback
#from django.test import TestCase
#uncomment this if you want to keep data after running tests
from unittest import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.test import Client
from server.models import Game, Move, Counter
