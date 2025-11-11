import pandas as pd
from utils import create_sample_excel

# Create sample Excel file
df = create_sample_excel()

# Save to Excel
df.to_excel('sample_input.xlsx', index=False)

print("Sample Excel file 'sample_input.xlsx' created successfully!")
print("\nSample data:")
print(df)
