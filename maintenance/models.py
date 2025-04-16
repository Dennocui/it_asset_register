from django.db import models
from assets.models import Asset

class MaintenanceType(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    recommended_frequency = models.PositiveIntegerField(help_text="In months", blank=True, null=True)
    
    def __str__(self):
        return self.name

class MaintenanceLog(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('on_hold', 'On Hold'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    maintenance_type = models.ForeignKey(MaintenanceType, on_delete=models.PROTECT)
    scheduled_date = models.DateField()
    completed_date = models.DateField(blank=True, null=True)
    technician = models.CharField(max_length=100, blank=True, null=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    description = models.TextField()
    resolution = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-scheduled_date']
    
    def __str__(self):
        return f"{self.asset} - {self.maintenance_type} on {self.scheduled_date}"
    
    @property
    def is_overdue(self):
        from datetime import date
        return self.status != 'completed' and date.today() > self.scheduled_date