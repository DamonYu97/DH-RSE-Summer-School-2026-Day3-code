import pandas as pd
import matplotlib.pyplot as plt

def read_preprocess(input_filename: str) -> pd.DataFrame:
    """
    Read and preprocessed data and return a dataframe
    :param input_filename: input eva data filename
    :return:
    """
    df = pd.read_json(input_filename, convert_dates=['date'], encoding='ascii')
    df['eva'] = df['eva'].astype(float)
    df.dropna(axis=0, subset=['duration', 'date'], inplace=True)  # drop rows where either duration or date is null
    return df


def create_crew_duration_subset(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create a subset of the dataframe that contains only crew and duration with each row having single crew.
    :param df: eva dataframe including rows with multiple crews.
    :return:
    """
    crew_duration_df = df.loc[:, ['crew', 'duration']] # subset of data with only columns crew and duration
    crew_duration_df.crew = crew_duration_df.crew.str.split(';').apply(lambda x: [i for i in x if i.strip()]) # anonymous function that takes a list of crew members and returns a list with whitespace stripped from names and empry stirngs removed
    crew_duration_df = crew_duration_df.explode('crew') # expand entries in a list-like column across multiple rows, making each element in the list a separate row and keeping/replicating values in other columns
    return crew_duration_df


def duration2hours(target_df: pd.DataFrame):
    # for the main dataframe - it should be a single reusable function
    hrs = []
    # Create a list of decimal values for duration in hours
    for duration in target_df['duration']:
        hr, minute = duration.split(":")
        hrs.append(int(hr) + int(minute) / 60)
    target_df['duration_hours'] = hrs


def plot_graph(df: pd.DataFrame, graph_output_filename: str):
    print(f'Plotting cumulative spacewalk duration and saving to {graph_output_filename}')
    plt.plot(df['date'], df['cumulative_time'], 'ko-')
    plt.xlabel('Year')
    plt.ylabel('Total time spent in space to date (hours)')
    plt.tight_layout()
    plt.savefig(graph_output_filename)
    plt.show()


def main():
    # TODO Inputs: this should be a command-line argument, not hardcoded
    input_filename = 'eva_data.json'
    # TODO Inputs: this should be a command-line argument, not hardcoded
    output_filename = 'eva_data.csv'

    print("--START--")

    print(f'Reading JSON data file {input_filename}')
    df = read_preprocess(input_filename)

    print(f'Saving data to CSV file {output_filename}')
    df.to_csv(output_filename, index=False, encoding='utf-8')

    # TODO DRY: duration-string-to-hours conversion is repeated again below
    subset = create_crew_duration_subset(df)
    duration2hours(subset)
    subset = subset.drop('duration', axis=1)
    subset = subset.groupby('crew').sum()

    # TODO Inputs: this should be a command-line argument, not hardcoded
    dur_out = 'duration_by_astronaut.csv'
    print(f'Saving to CSV file {dur_out}')
    subset.to_csv(dur_out, index=True, encoding='utf-8')

    df.sort_values('date', inplace=True)

    # TODO DRY: Duplicate of the hours-conversion logic above - violates DRY
    duration2hours(df)
    df['cumulative_time'] = df['duration_hours'].cumsum()

    # TODO Inputs: graph save location should be a command-line argument, not hardcoded
    graph_output_filename = 'cumulative_eva_graph.png'
    plot_graph(df, graph_output_filename)

    print("--END--")

if __name__ == '__main__':
    main()