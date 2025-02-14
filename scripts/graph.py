import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Example data: rows are top X% of houses, columns are tax rates
top_percentages = np.array([1, 5, 10, 15, 20])  # Top X% of houses

low, high = 0.0117143563, 0.015
range_values = np.linspace(low, high, num=10)  # Create 10 evenly spaced values
tax_values = np.random.choice(range_values, 5, replace=False)  # Pick 2
print(tax_values)


# Simulating revenue data (replace with actual calculations)
revenue_data = {rate: (np.log1p(top_percentages) * rate * 1000) for rate in tax_values}
df = pd.DataFrame(revenue_data, index=top_percentages)

# Plotting
plt.figure(figsize=(10, 6))
for rate in tax_values:
    plt.plot(df.index, df[rate], marker='o', label=f'Tax Rate: {rate*100:.1f}%')

plt.xlabel("Top Percentage of Houses Affected")
plt.ylabel("Revenue Generated")
plt.title("Revenue vs. Top Percentage of Houses Affected at Different Tax Rates")
plt.legend()
plt.grid(True)
plt.show()
