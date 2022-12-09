from django.contrib import admin
from excel_api import models



class ExcelDataAdmin(admin.ModelAdmin):
    list_display = ('id', 'time', 'valid_action', 'symbol', 'total_position', 'initial_margin', 'total_deposit', 'order_price', 'stop_loss', 'take_profit', 'contract_type', 'token_quantity', 'leverage', 'liquidation_price')
    list_display_links = ('id', 'time', 'valid_action', 'symbol', 'total_position', 'initial_margin', 'total_deposit', 'order_price', 'stop_loss', 'take_profit', 'contract_type', 'token_quantity', 'leverage', 'liquidation_price')
    list_filter = ('time', 'valid_action', 'symbol', 'total_position', 'initial_margin', 'contract_type', 'token_quantity')
    list_per_page = 20
# Register your models here.
admin.site.register(models.UserProfile)
admin.site.register(models.ExcelData, ExcelDataAdmin)
admin.site.register(models.ConstantDatas)