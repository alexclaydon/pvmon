from libs.logger import local_logger
from matplotlib import pyplot as plt


def visualise_sensors(df):
    """
    :param df: dataframe returned by transform_data()
    :return: plots to stdout
    """
    # fig, ax = plt.subplots()
    plt.style.use("ggplot")
    df.loc[:, "S01":"S03"].groupby(level=(1, 0)).mean().stack().unstack(1).unstack(
        1
    ).plot(
        kind="hist",
        subplots=True,
        # stacked=True,
        colormap="viridis",
        layout=(7, 3),
        figsize=(12, 12),
        sharex=False,
        # sharey='row',
        bins=100,
        # ax=ax
    )
    plt.show()


def alt1_vis_sensors(df):
    """
    :param df: dataframe returned by transform_data()
    :return: plots to stdout
    """
    fig, ax = plt.subplots()
    plt.style.use("ggplot")
    df.loc[:, "S01":"S03"].groupby(["project_name"]).plot(
        kind="hist",
        subplots=True,
        # layout=(8, 3),
        # figsize=(15, 15),
        # sharex=False,
        # sharex='col',
        # sharey='row',
        # colormap='Blues',
        # alpha=0.5,
        # orientation='horizontal',
        # cumulative=True,
        # stacked=True,
        bins=30,
        # style='k--',  # Makes everything b&w
        # title='sancon1',
        # logy=True,
        ax=ax,
    )
    ax.set(
        xlabel="kWh Contribution to Total (%)", ylabel="Frequency", xlim=(0.1, 0.4),
    )
    fig.show()
    # plt.show()


def alt2_vis_project(df, project):
    """
    :param df: dataframe returned by transform_data()
    :param project: string matching the name of the relevant project
    :return: plots to stdout
    """
    select = df.loc[df.index.get_level_values(0).isin([project])]
    fig, ax = plt.subplots()
    plt.style.use("ggplot")
    select.loc[:, "S01":"S03"].plot(
        kind="hist",
        # subplots=True,
        # layout=(3, 3),
        # figsize=(10, 10),
        # sharex=False,
        # colormap='Blues',
        # alpha=0.5,
        # orientation='horizontal',
        # cumulative=True,
        stacked=True,
        bins=25,
        # style='k--',  # Makes everything b&w
        # title=project,
        # logy=True,
        ax=ax,
    )
    ax.set(
        xlabel="kWh Contribution to Total (%)", ylabel="Frequency", xlim=(0.05, 0.45),
    )
    fig.show()
    # plt.show()
