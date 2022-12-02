from django.contrib import admin
from .models import Observation, Component

admin.register(Component)
admin.register(Observation)
