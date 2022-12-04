from django.contrib import admin
from excel_api import models

# Register your models here.
admin.site.register(models.UserProfile)
admin.site.register(models.ExcelData)
admin.site.register(models.ConstantDatas)