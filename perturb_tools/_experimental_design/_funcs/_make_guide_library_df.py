
from ._annotate_protospacer import _annotate_protospacer
import pandas as pd
import numpy as np

def _reformat_peaks_annotations(pam_loci_df, peak_bins):

    """
    Reformat dataframe of peak-assigned pam loci to a neater df.
    Parameters:
    -----------
    pam_loci_df
        dataframe matching all PAM loci to a peak
    peak_bins
        loci of peak "bins"
    Returns:
    --------
    df
        *cleaned* dataframe matching all PAM loci to a peak
    """

    pam_loci_df = pam_loci_df.dropna()

    left, right = peak_bins[0::2], peak_bins[1::2]

    pams_in_peaks_left = np.array([])
    pams_in_peaks_right = np.array([])
    index = np.array([])

    for a, i in enumerate(pam_loci_df[1]):

        if i.left in left:
            pams_in_peaks_left = np.append(pams_in_peaks_left, i.left)
        if i.right in right:
            pams_in_peaks_right = np.append(pams_in_peaks_right, i.right)
            index = np.append(index, pam_loci_df[0].values[a])

    df = pd.DataFrame(
        np.vstack([index, pams_in_peaks_left, pams_in_peaks_right]).T,
        columns=["PAM_loci", "ATAC_peak_left", "ATAC_peak_right"],
    )
    
    return df


def _assemble_pam_loci_df(forward, reverse, chromosome_peaks, chromosome_key="Chromosome"):

    """
    Bins PAM loci into peak "bins". Mindful of strand information. Uses adjusted reverse strand loci values.
    Parameters:
    -----------
    forward
        numpy array of forward strand PAM loci
    reverse
        numpy array of reverse strand PAM loci. Should already be (3'-5') adjusted.
    chromosome_peaks
        pandas DataFrame containing the start and stop location of each peak.
    Returns:
    --------
    df
        cleaned DataFrame containing PAM loci, strand assignment, and peak annotation.
    """

 
    forward_pam_peak_assigned, peak_widths_forward = _assign_pam_loci_to_peaks(
        forward, chromosome_peaks
    )

    reverse_pam_peak_assigned, peak_widths_reverse = _assign_pam_loci_to_peaks(
        reverse, chromosome_peaks
    )

    reformated_forward_df = _reformat_peaks_annotations(
        forward_pam_peak_assigned, peak_widths_forward
    )
    reformated_reverse_df = _reformat_peaks_annotations(
        reverse_pam_peak_assigned, peak_widths_reverse
    )

    # add strand info
    reformated_forward_df["strand"] = "+"
    reformated_reverse_df["strand"] = "-"

    df = (
        pd.concat([reformated_forward_df, reformated_reverse_df])
        .sort_values("PAM_loci")
        .reset_index(drop=True)
    )

    df = _add_guide_peak_info(df)
    df[chromosome_key] = chromosome_peaks[chromosome_key].unique()[0]
    cols = df.columns.tolist()[-1:] + df.columns.tolist()[:-1]
    df = df[cols]

    df = df.reset_index(drop=True)

    return df

def _make_guide_library_df(forward_pams, reverse_pams, peak_df, chrom_seqs, chromosome_key="Chromosome"):

    """"""

    appended_dfs = []

    for i, chrom in enumerate(peak_df[chromosome_key].unique()):

        df = _assemble_pam_loci_df(
            forward_pams[i],
            reverse_pams[i],
            peak_df.loc[peak_df[chromosome_key].astype(str) == chrom],
        )

        df = _annotate_protospacer(df, chrom_seqs[i])
        appended_dfs.append(df)

    df = pd.concat(appended_dfs)
    df = df.drop_duplicates("protospacer")
    df = df.reset_index(drop=True)

    return df