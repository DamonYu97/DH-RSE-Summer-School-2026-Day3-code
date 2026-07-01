import argparse

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
    # drop rows where either duration or date is null
    df.dropna(axis=0, subset=['duration', 'date'], inplace=True)
    return df


def create_crew_duration_subset(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create a subset of the dataframe that contains only crew and duration with each row having single crew.
    :param df: eva dataframe including rows with multiple crews.
    :return:
    """
    # subset of data with only columns crew and duration
    crew_duration_df = df.loc[:, ['crew', 'duration']]
    # anonymous function that takes a list of crew members and returns a list with whitespace stripped from names and empry stirngs removed
    crew_duration_df.crew = crew_duration_df.crew.str.split(';').apply(lambda x: [i for i in x if i.strip()])
    # expand entries in a list-like column across multiple rows, making each element in the list a separate row and keeping/replicating values in other columns
    crew_duration_df = crew_duration_df.explode('crew')
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


def main(args):
    input_filename = args.input_filename
    output_filename = args.output_filename

    print("--START--")

    print(f'Reading JSON data file {input_filename}')
    df = read_preprocess(input_filename)

    print(f'Saving data to CSV file {output_filename}')
    df.to_csv(output_filename, index=False, encoding='utf-8')

    subset = create_crew_duration_subset(df)
    duration2hours(subset)
    subset = subset.drop('duration', axis=1)
    subset = subset.groupby('crew').sum()

    dur_out = args.crew_duration_filename
    print(f'Saving to CSV file {dur_out}')
    subset.to_csv(dur_out, index=True, encoding='utf-8')

    df.sort_values('date', inplace=True)

    duration2hours(df)
    df['cumulative_time'] = df['duration_hours'].cumsum()

    graph_output_filename = args.graph_output_filename
    plot_graph(df, graph_output_filename)

    print("--END--")

if __name__ == '__main__':
    # parse cli arguments
    args = argparse.ArgumentParser()
    args.add_argument('-i', '--input_filename', required=True)
    args.add_argument('-o', '--output_filename', required=True)
    args.add_argument('-cd', '--crew_duration_filename', required=True)
    args.add_argument('-g', '--graph_output_filename', required=True)
    args = args.parse_args()
    # main process
    main(args)