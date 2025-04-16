from django.db import models

class Company(models.Model):
    name = models.CharField(max_length=100)
    tax_id = models.CharField(max_length=50, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    contact_email = models.EmailField(blank=True, null=True)
    contact_phone = models.CharField(max_length=20, blank=True, null=True)
    logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)
    contract_start_date = models.DateField(blank=True, null=True)
    contract_end_date = models.DateField(blank=True, null=True)
    
    def __str__(self):
        return self.name

class Site(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    address = models.TextField()
    primary_contact = models.CharField(max_length=100, blank=True, null=True)
    
    def __str__(self):
        return f"{self.company.name} - {self.name}"

class Department(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    cost_center = models.CharField(max_length=50, blank=True, null=True)
    
    def __str__(self):
        return f"{self.company.name} - {self.name}"