from django.db import models
from decimal import Decimal
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
class LeaseContract(models.Model):
   
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
        ('Amendment', 'Amendment'),
    ]

    code = models.CharField(max_length=50, unique=True)
    lease_type = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    leasor_name = models.CharField(max_length=255)
    contract_date = models.DateField()
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='Active'
    )

    class Meta:
        db_table = 'lease_contract'

    def __str__(self):
        return f"{self.code} - {self.leasor_name}"


class LeaseFinancial(models.Model):
    PERIOD_CHOICES = [
        ('Year', 'Year'),
        ('Month', 'Month'),
    ]
    
    COMPUTATION_CHOICES = [
        ('Month', 'Month'),
        ('Year', 'Year'),
        ('Quaterly', 'Quaterly'),
        ('Half of Year', 'Half of Year'),
    ]

    lease = models.OneToOneField(
        LeaseContract, 
        on_delete=models.CASCADE, 
        related_name='financial'
    )
    contract_amount = models.DecimalField(max_digits=20, decimal_places=2)
    deposit = models.DecimalField(max_digits=20, decimal_places=2)
    present_value = models.DecimalField(max_digits=20, decimal_places=2, editable=False, default=0.0)
    down_payment = models.DecimalField(max_digits=20, decimal_places=2)
    other_cost = models.DecimalField(max_digits=20, decimal_places=2)
    dismantling_cost = models.DecimalField(max_digits=20, decimal_places=2)
    currency = models.CharField(max_length=10)
    home_currency = models.CharField(max_length=10)
    exchange_rate = models.DecimalField(max_digits=15, decimal_places=4)
    start_date = models.DateField()
    end_date = models.DateField()
    lease_term = models.IntegerField()
    lease_period = models.CharField(max_length=10, choices=PERIOD_CHOICES)
    discount_rate = models.FloatField() 
    # extensions = models.BooleanField(default=False)
    payment_amount = models.DecimalField(max_digits=20, decimal_places=2)
    payment_period = models.CharField(max_length=10, choices=PERIOD_CHOICES)
    computation = models.CharField(max_length=20, choices=COMPUTATION_CHOICES)
    changing_date = models.DateField(null=True, blank=True)
    changing_amount = models.DecimalField(max_digits=20, decimal_places=2, default=0.0)
    reason = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'lease_financial'

    def get_calculated_pv(self):
        total_pv = Decimal('0.00')
        discount_rate = Decimal(str(self.discount_rate)) / 100

        is_yearly = self.computation.lower() == 'year'
        total_periods = self.lease_term if is_yearly else self.lease_term * 12
        
        # Periodic rate တွက်ချက်ခြင်း
        # periodic_rate = discount_rate if is_yearly else (Decimal('1') + discount_rate) ** (Decimal('1')/12) - 1
        if is_yearly:
            periodic_rate = discount_rate
        else:
           
            periodic_rate = discount_rate / 12
        
        change_at_period = None
        if self.changing_date:
            diff = relativedelta(self.changing_date, self.start_date)
            total_months_diff = diff.years * 12 + diff.months
            change_at_period = (total_months_diff // 12) if is_yearly else total_months_diff

        for t in range(1, total_periods + 1):
            
            current_payment = Decimal(str(self.payment_amount))
            if change_at_period and t > change_at_period:
                current_payment = Decimal(str(self.changing_amount))

            
            pv_of_period = current_payment / ((Decimal('1') + periodic_rate) ** t)
            total_pv += pv_of_period

        
        total_pv += Decimal(str(self.down_payment))
        return total_pv.quantize(Decimal('0.01'))

    def save(self, *args, **kwargs):
        self.present_value = self.get_calculated_pv()
        super().save(*args, **kwargs)

    def get_amortization_schedule(self):
        
        schedule = []
        
        remaining_balance = self.present_value 
        
        discount_rate = Decimal(str(self.discount_rate)) / 100
        is_yearly = self.computation.lower() == 'year'
        periodic_rate = discount_rate / (1 if is_yearly else 12)
        total_periods = self.lease_term if is_yearly else self.lease_term * 12

        change_at_period = None
        if self.changing_date:
            diff = relativedelta(self.changing_date, self.start_date)
            months = diff.years * 12 + diff.months
            change_at_period = (months // 12) if is_yearly else months

        current_date = self.start_date
        for t in range(1, total_periods + 1):
            interest_expense = remaining_balance * periodic_rate
            
            payment = Decimal(str(self.payment_amount))
            if change_at_period and t > change_at_period:
                payment = Decimal(str(self.changing_amount))

            principal_reduction = payment - interest_expense
            opening_bal = remaining_balance
            remaining_balance -= principal_reduction
            
            
            if is_yearly:
                current_date = current_date + relativedelta(years=1)
            else:
                current_date = current_date + relativedelta(months=1)

            schedule.append({
                "period": t,
                "date": current_date.strftime('%Y-%m-%d'),
                "opening_balance": round(opening_bal, 2),
                "payment": round(payment, 2),
                "interest": round(interest_expense, 2),
                "principal": round(principal_reduction, 2),
                "closing_balance": round(max(0, remaining_balance), 2)
            })
        return schedule

    def save(self, *args, **kwargs):
        
        self.present_value = self.get_calculated_pv()
        super().save(*args, **kwargs)


    
