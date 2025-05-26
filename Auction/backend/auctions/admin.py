from django.contrib import admin
from .models import Auction, Bid, Item, ItemImage, Watchlist

class ItemImageInline(admin.TabularInline):
    model = ItemImage
    extra = 1

class ItemAdmin(admin.ModelAdmin):
    inlines = [ItemImageInline]
    list_display = ('name', 'auction', 'category', 'condition')
    search_fields = ('name', 'description', 'category')
    list_filter = ('category', 'condition')

class AuctionAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'start_time', 'end_time', 'current_price', "company")
    list_filter = ('status', 'company')
    search_fields = ('title', 'description', 'company__name')
    date_hierarchy = 'start_time'
    raw_id_fields = ('company',)

class BidAdmin(admin.ModelAdmin):
    list_display = ('auction', 'user', 'amount', 'is_winning', 'created_at')
    list_filter = ('is_winning', 'auction')
    search_fields = ('user__username', 'auction__title')
    date_hierarchy = 'created_at'
    raw_id_fields = ('auction', 'user')

class WatchlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'auction', 'created_at')
    list_filter = ('auction',)
    search_fields = ('user__username', 'auction__title')
    raw_id_fields = ('user', 'auction')

admin.site.register(Auction, AuctionAdmin)
admin.site.register(Bid, BidAdmin)
admin.site.register(Item, ItemAdmin)
admin.site.register(Watchlist, WatchlistAdmin)
