import pandas as pd
import matplotlib.pyplot as plt
import re

# TODO Inputs: this should be a command-line argument, not hardcoded
input_filename = 'eva_data.json'
# TODO Inputs: this should be a command-line argument, not hardcoded
output_filename = 'eva_data.csv'

# TODO: Unused variable - candidate for removal
fieldnames = ("EVA number", "Country", "Crew", "Vehicle", "Date", "Duration", "Purpose")

print("--START--")

print(f'Reading JSON data file {input_filename}')
df = pd.read_json(input_filename, convert_dates=['date'], encoding='ascii')
df['eva'] = df['eva'].astype(float)
df.dropna(axis=0, subset=['duration', 'date'], inplace=True)  # drop rows where either duration or date is null

print(f'Saving data to CSV file {output_filename}')
df.to_csv(output_filename, index=False, encoding='utf-8')

# TODO Descriptive comment: add an explanation of that the 3 lines below do
subset = df.loc[:, ['crew', 'duration']] # subset of data with only columns crew and duration
subset.crew = subset.crew.str.split(';').apply(lambda x: [i for i in x if i.strip()]) # anonymous function that takes a list of crew members and returns a list with whitespace stripped from names and empry stirngs removed
subset = subset.explode('crew') # expand entries in a list-like column across multiple rows, making each element in the list a separate row and keeping/replicating values in other columns

# TODO DRY: duration-string-to-hours conversion is repeated again below
# for the main dataframe - it should be a single reusable function
hrs = []
# Create a list of decimal values for duration in hours
for duration in subset['duration']:
    hr, minute = duration.split(":")
    hrs.append(int(hr) + int(minute) / 60)
subset['duration_hours'] = hrs
subset = subset.drop('duration', axis=1)
subset = subset.groupby('crew').sum()

# TODO Inputs: this should be a command-line argument, not hardcoded
dur_out = 'duration_by_astronaut.csv'
print(f'Saving to CSV file {dur_out}')
subset.to_csv(dur_out, index=True, encoding='utf-8')

df.sort_values('date', inplace=True)

# TODO DRY: Duplicate of the hours-conversion logic above - violates DRY
hrs2 = []
for duration in df['duration']:
    hr, minute = duration.split(":")
    hrs2.append(int(hr) + int(minute) / 60)
df['duration_hours'] = hrs2

df['cumulative_time'] = df['duration_hours'].cumsum()


# TODO Inputs: graph save location should be a command-line argument, not hardcoded
graph_output_filename = 'cumulative_eva_graph.png'
print(f'Plotting cumulative spacewalk duration and saving to {graph_output_filename}')
plt.plot(df['date'], df['cumulative_time'], 'ko-')
plt.xlabel('Year')
plt.ylabel('Total time spent in space to date (hours)')
plt.tight_layout()
plt.savefig(graph_output_filename)
plt.show()


# TODO: Unused function - candidate for removal
# or for wiring into the analysis (left as unused/dead code on purpose)
def calculate_crew_size(crew):
    if crew.split() == []:
        return None
    else:
        return len(re.split(r';', crew)) - 1

print("--END--")