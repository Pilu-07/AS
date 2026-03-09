import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta

def generate_sales_data(num_rows=100000, output_file='sales_data.csv'):
    print(f"Generating {num_rows} rows of sales data...")
    
    # Define possible values for categorical columns
    products = ['Laptop', 'Smartphone', 'Tablet', 'Headphones', 'Monitor', 'Keyboard', 'Mouse', 'Webcam', 'Microphone', 'Speakers']
    regions = ['North America', 'South America', 'Europe', 'Asia', 'Africa', 'Oceania']
    customer_segments = ['Consumer', 'Corporate', 'Home Office', 'Small Business']
    
    # Generate dates (last 2 years)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=730)
    
    dates = [start_date + timedelta(days=np.random.randint(0, 730)) for _ in range(num_rows)]
    
    # Generate data
    data = {
        'date': dates,
        'product': np.random.choice(products, num_rows),
        'region': np.random.choice(regions, num_rows),
        'customer_segment': np.random.choice(customer_segments, num_rows),
        'marketing_spend': np.random.uniform(50, 5000, num_rows).round(2),
        'revenue': np.random.uniform(100, 10000, num_rows).round(2),
    }
    
    df = pd.DataFrame(data)
    
    # Calculate profit based on revenue and marketing spend, plus some noise
    df['profit'] = (df['revenue'] * np.random.uniform(0.1, 0.4, num_rows) - df['marketing_spend'] * 0.2).round(2)
    
    # Sort by date
    df = df.sort_values('date')
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
    
    df.to_csv(output_file, index=False)
    print(f"Dataset saved to {output_file}")
    
if __name__ == "__main__":
    generate_sales_data(100000, 'tests/e2e/data/sales_data.csv')
