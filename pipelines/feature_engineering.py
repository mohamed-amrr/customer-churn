class FeatureEngineering:
    def __init__(self, df):
        self.df = df
    
    def handle(self):
        self.df['AvgMonthlySpend'] = self.df['TotalCharges'] / (self.df['tenure'] + 1)
        self.df['ChargeRatio'] = self.df['MonthlyCharges'] / (self.df['TotalCharges'] + 1)
        self.df['IsNewCustomer'] = (self.df['tenure'] < 6).astype(int)
        return self.df