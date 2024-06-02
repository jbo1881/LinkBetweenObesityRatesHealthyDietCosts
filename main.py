import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import pearsonr

# Read FAOSTAT data
faostat = pd.read_excel('FAOSTAT.xls')
country = faostat['Area']
cost = faostat['Value']

# Read the CSV file, allowing for flexible parsing
obesity = pd.read_csv('obesity.csv', header=None, delimiter=',|,"', engine='python')

# Select only the relevant columns
obesity_combined = obesity.iloc[:, :2]

# Ensure the column names match for the join
obesity_combined.columns = ['Country', 'ObesityRateByCountry']
obesity_combined = obesity_combined.iloc[1:]
obesity_combined['Country'] = obesity_combined['Country'].str.lstrip('"')
obesity_combined = obesity_combined.dropna()

# Create healthy_diet_obesity DataFrame
healthy_diet_obesity = pd.DataFrame({'Country': country, 'HealthyDietCost': cost})
healthy_diet_obesity = healthy_diet_obesity.dropna()

country_mapping = {
    "United States of America": "United States",
    "Bolivia (Plurinational State of)": "Bolivia",
    "Brunei Darussalam": "Brunei",
    "Cabo Verde": "Cape Verde",
    "China, Hong Kong SAR": "China",
    "Congo": "Republic of the Congo",
    "Lao People's Democratic Republic": "Laos",
    "Netherlands (Kingdom of the)": "Netherlands",
    "Republic of Korea": "South Korea",
    "Republic of Moldova": "Moldova",
    "Russian Federation": "Russia",
    "Türkiye": "Turkey",
    "United Republic of Tanzania": "Tanzania",
    "Viet Nam": "Vietnam",
    "United Kingdom of Great Britain and Northern Ireland": "United Kingdom",
    "Iran (Islamic Republic of)": "Iran"
    # Add more mappings as needed
}

# Apply the mapping to standardize country names in healthy_diet_obesity
healthy_diet_obesity['Country'] = healthy_diet_obesity['Country'].replace(country_mapping)

# Perform the left join
result = healthy_diet_obesity.merge(obesity_combined, on='Country', how='left')

# Fill missing values with data from https://data.worldobesity.org/rankings/
result.loc[result['Country'] == 'Spain', 'ObesityRateByCountry'] = 19.39
result.loc[result['Country'] == 'Tanzania', 'ObesityRateByCountry'] = 6.73
result.loc[result['Country'] == 'Tunisia', 'ObesityRateByCountry'] = 19.92
result.loc[result['Country'] == 'Suriname', 'ObesityRateByCountry'] = 19.67
result.loc[result['Country'] == 'South Korea', 'ObesityRateByCountry'] = 8.82
result.loc[result['Country'] == 'Peru', 'ObesityRateByCountry'] = 23.62
result.loc[result['Country'] == 'Finland', 'ObesityRateByCountry'] = 21.88

# Retrieve the rows where 'ObesityRateByCountry' column has NaN values
countries_with_nan = result[result['ObesityRateByCountry'].isna()]['Country']

# Read population data
population = pd.read_csv('world_population.csv')
population = population[['Country/Territory', '2022 Population']]
population.rename(columns={'Country/Territory': 'Country', '2022 Population': 'Population'}, inplace=True)

# Perform the left join with the result DataFrame
result = result.merge(population, on='Country', how='left')
result = result.dropna()

# Ensure all values in the 'Country' column are strings
result['Country'] = result['Country'].astype(str)

# Ensure Population is numeric
result['Population'] = pd.to_numeric(result['Population'])

# Convert 'ObesityRateByCountry' to numeric
result['ObesityRateByCountry'] = pd.to_numeric(result['ObesityRateByCountry'])

# Check data types and non-null values
print(result.dtypes)
print(result.isna().sum())

# Calculate Pearson correlation coefficient
correlation, p_value = pearsonr(result['HealthyDietCost'], result['ObesityRateByCountry'])

# Display the correlation
print(f'Pearson correlation coefficient: {correlation}')
print(f'P-value: {p_value}')

# Chart
plt.figure(figsize=(12, 8))
sc = sns.scatterplot(
    data=result,
    x='HealthyDietCost',
    y='ObesityRateByCountry',
    size='Population',
    hue='Country',
    alpha=0.6,
    palette='viridis',
    sizes=(20, 2000),  
    legend=False 
)

# Annotate each point with the country name for countries with population > 30,000,000 or < 2,000,000
filtered_result = result[(result['Population'] > 30000000) | (result['Population'] < 2000000)]
for i in range(filtered_result.shape[0]):
    plt.text(
        x=filtered_result['HealthyDietCost'].iloc[i],
        y=filtered_result['ObesityRateByCountry'].iloc[i],
        s=filtered_result['Country'].iloc[i],
        fontdict=dict(color='black', size=6),
        bbox=dict(facecolor='white', alpha=0.5, edgecolor='none', pad=1)
    )

plt.xlabel('Healthy Diet Cost (PPP dollar per person per day)')
plt.ylabel('Obesity Rate (%)')
plt.title('Share of Adult Obese vs. Daily Healthy Diet Cost, 2024')

# Create a legend for the population sizes with more separation
legend_sizes = [10000000, 100000000, 1000000000]
legend_labels = [f'{int(size / 1000000)} M' for size in legend_sizes]
legend_handles = [
    plt.scatter([], [], s=size / 1000000, c='gray', alpha=0.5, edgecolors='w', linewidth=0.5) 
    for size in legend_sizes
]
plt.legend(legend_handles, legend_labels, title='Population Size', loc='upper right', fontsize=6, frameon=False, borderpad=3, handletextpad=2)


plt.grid(True, which='both', lw=0.5)

# Save the plot as a PNG file
plt.savefig('obesity_vs_diet_cost.png')

# Show the plot
plt.show()
