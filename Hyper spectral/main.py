from detection_algo import matched_filter, ace, rx
from ArtificialHyperspectral_class import ArtificialHyperspectralCube, HyperSpectralCube, ArtificialHSC
from plot_detection_algo import plot_stats, calc_stats
import spectral as spy
from local_mean_covariance import get_m8, get_cov8
import numpy as np
import warnings
import matplotlib.pyplot as plt
import datetime
from pathlib import Path


def crop_hypercube(hypercube, target_dimensions):
    return hypercube[:target_dimensions[0], :target_dimensions[1], :target_dimensions[2]]


def remove_constant_dimensions(cube):
    # Find indices of dimensions with variability
    non_constant_indices = np.where(np.std(cube, axis=(0, 1)) != 0)[0]
    return cube[:, :, non_constant_indices]


warnings.filterwarnings('ignore')

if __name__ == "__main__":
    ######################################
    # SIMULATION FOR COMCAS PAPER
    ######################################
    #datasets = {"TAIT": r'C:\Users\97252\Desktop\SCHOOL\project\raw_4432_rd_rf_or.hdr'}
    datasets = {"RIT": r'C:\Users\97252\Desktop\SCHOOL\project\self_test_rad.hdr'}
    methods = ["Suggested method", "Constant2", "MLE"]
    print('**************************************************************************************')
    print("Starting Simulation at ", datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S'))
    print('Datasets: ', list(datasets.keys()))
    print('Methods: ', methods)
    print('**************************************************************************************')

    target_dimensions = (600, 600, 272)

    for dataset_name, dataset_header in datasets.items():
        original_data = HyperSpectralCube(dataset_header)

        # Print original dimensions
        print(f"Original Dimensions ({dataset_name}): {original_data.cube.shape}")

        # Remove constant dimensions
        original_data.cube = remove_constant_dimensions(original_data.cube)

        # Crop the hypercube
        cropped_data = crop_hypercube(original_data.cube, target_dimensions)

        # Update dimensions and recalculate mean and covariance
        original_data.cube = cropped_data
        original_data.dimensions = cropped_data.shape

        # Print cropped dimensions
        print(f"Cropped Dimensions ({dataset_name}): {original_data.cube.shape}")

        original_data.calc_mean()
        original_data.calc_cov()

        pca_data = original_data.pca_transform()
        pca_data.calc_mean()
        pca_data.calc_cov()

        gaussian_data = ArtificialHSC(pca_data,
                                      original_data.eigenvectors,
                                      original_data.eigenvalues,
                                      from_gaussian=True)
        gaussian_data.calc_mean()
        gaussian_data.calc_cov()

        mf_res_x = matched_filter(0.065, original_data.cube, original_data.mean, original_data.cov,
                                  original_data.cube[4, 2].reshape(1, 1, -1))

        mf_res_g = matched_filter(0.065, gaussian_data.cube, gaussian_data.mean, gaussian_data.cov,
                                  original_data.cube[4, 2].reshape(1, 1, -1))

        histogram_wt_x, histogram_nt_x, fpr_x, tpr_x, thresholds_x = calc_stats(mf_res_x[0], mf_res_x[1])
        histogram_wt_g, histogram_nt_g, fpr_g, tpr_g, thresholds_g = calc_stats(mf_res_g[0], mf_res_g[1])

        for method in methods:
            print('Method: ', method)
            print('**************************************************************************************')
            pca_data.calc_nu(method)
            pca_data.plot_nu(f'{dataset_name} DOF Estimation - {method}')
            # artificial data
            artifical_data = ArtificialHSC(pca_data, original_data.eigenvectors, original_data.eigenvalues)

            # MF results
            mf_res_q = matched_filter(0.065, artifical_data.cube, artifical_data.mean, artifical_data.cov,
                                      original_data.cube[4, 2].reshape(1, 1, -1))

            histogram_wt_q, histogram_nt_q, fpr_q, tpr_q, thresholds_q = calc_stats(mf_res_q[0], mf_res_q[1])

            # plots: LOG scale histogram and ROC curve
            # log scale histogram
            plt.figure(figsize=(10, 5))
            plt.plot(histogram_wt_x[1][1:], np.log10(histogram_wt_x[0]),
                     label='Original data_WT', color='g', linewidth=3)
            plt.plot(histogram_nt_x[1][1:], np.log10(histogram_nt_x[0]),
                     "--", label='Original data_NT', color='g', linewidth=3)
            plt.plot(histogram_wt_g[1][1:], np.log10(histogram_wt_g[0]),
                     label='Gaussian artificial data_WT', color='b', linewidth=2)
            plt.plot(histogram_nt_g[1][1:], np.log10(histogram_nt_g[0]),
                     "--", label='Gaussian artificial data_NT', color='b', linewidth=2)
            plt.plot(histogram_wt_q[1][1:], np.log10(histogram_wt_q[0]),
                     label='Artificial data_WT', color='r', linewidth=2)
            plt.plot(histogram_nt_q[1][1:], np.log10(histogram_nt_q[0]),
                     "--", label='Artificial data_NT', color='r', linewidth=2)
            plt.title(f'Log10 Histogram Results')
            plt.ylabel('log10(Number of samples)')
            plt.xlabel('Detection score')
            plt.grid()
            plt.legend(loc='upper left')
            plt.xlim(-1000, 1000)
            plt.savefig(
                f"plots/{dataset_name}_{method}_log10_histogram_{datetime.datetime.now().strftime('_%d_%m_%Y__%H_%M_%S')}.png")
            plt.show()

            # ROC curve
            plt.plot(fpr_x, tpr_x, label='Original data', color='g', linewidth=3)
            plt.plot(fpr_g, tpr_g, label='Gaussian artificial data', color='b', linewidth=2)
            plt.plot(fpr_q, tpr_q, label='Artificial data', color='r', linewidth=2)
            plt.title(f'ROC curve with limited pfa = 0.01')
            plt.ylabel('TPR')
            plt.xlabel('FPR')
            plt.grid()
            plt.legend(loc='lower right')
            plt.xlim(0, 0.01)
            plt.ylim(0, 1)
            plt.savefig(
                f"plots/{dataset_name}_{method}_ROC_curve_{datetime.datetime.now().strftime('_%d_%m_%Y__%H_%M_%S')}.png")
            plt.show()

            print("DONE : for data ", dataset_name, " and method ", method)
            print('**************************************************************************************')
        print("**************************************************************************************")
        print("DONE : for data ", dataset_name)
        print("**************************************************************************************")
        print("Simulation Done.")
