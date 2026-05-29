from django.contrib import admin
from .models import Task

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    # 1. Columns displayed in the main table list grid view
    list_display = ('title', 'assigned_to', 'priority', 'due_date', 'status', 'created_at')
    
    # 2. Right-hand interactive filter panel choices mapping matrix
    list_filter = ('status', 'priority', 'due_date')
    
    # 3. Live text search fields tracking column inputs
    search_fields = ('title', 'description', 'assigned_to_email', 'assigned_to__email', 'assigned_to__full_name')
    
    # 4. Chronological date hierarchy drill-down navigation bar
    date_hierarchy = 'due_date'
    
    # 5. Default sorting sequence matching your Mongoose requirements
    ordering = ('due_date', '-created_at')

    # 6. Automate setting the 'created_by' field to the current logged-in admin user on save
    def save_model(self, request, obj, form, change):
        if not change: # If this is a brand-new task creation row
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
