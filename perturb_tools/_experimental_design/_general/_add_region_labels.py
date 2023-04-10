import numpy as np
import pandas as pd


def _add_region_labels(guide_df: pd.DataFrame):
    """"""

    regions = np.array([])

    for n, region in enumerate(guide_df.groupby("region_left")):
        regions = np.append(regions, np.full(len(region[1]), n))

    guide_df["region"] = regions

    return guide_df
