from django.contrib import admin
from .models.ball import Ball
from .models.video import BallVideo
from .models.fielding import BallFielding
# Register your models here.
admin.site.register(Ball)
admin.site.register(BallVideo)
admin.site.register(BallFielding)
