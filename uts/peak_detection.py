# coding: utf-8

__author__ = 'Mário Antunes'
__version__ = '0.1'
__email__ = 'mariolpantunes@gmail.com'
__status__ = 'Development'


import numpy as np
import math


from uts import zscore, thresholding


def all_peaks(points):

    filter_array = [False]

    for i in range(1, len(points) - 1):
        y0 = points[i-1][1]
        y = points[i][1]
        y1 = points[i+1][1]

        if y0 < y and y > y1:
            filter_array.append(True)
        else:
            filter_array.append(False)
    
    filter_array.append(False)
    return np.array(filter_array)


def significant_peaks(points, peaks_idx, h=1.0):
    peaks = points[peaks_idx]
    m = np.mean(peaks, axis=0)[1]
    s = np.std(peaks, axis=0)[1]

    significant = []

    for i in range(0, len(points)):
        if peaks_idx[i]:
            value = points[i][1]
            if value > (m+h*s):
                significant.append(True)
            else:
                significant.append(False)
        else:
            significant.append(False)

    return np.array(significant)

def find_next_tau(points, i, tau):
    if i == len(points)-1:
        return i
    
    durations = points[i+1:,0] - points[i:-1,0]
    cumulative_durations = np.cumsum(durations)
    idx = cumulative_durations[cumulative_durations>tau]
    idx = np.argmax(cumulative_durations>tau)
    
    if idx == 0:
        return len(points)-1
    
    return i+idx+1


def zscore_peaks_values(points, peaks_idx):
    peaks = points[peaks_idx]

    scores = []

    # k current peak
    k = 0
    # left part of the sliding window
    left = 0
    # i current point
    for i in range(0, len(points)):
        if peaks_idx[i]:
            # Zscore from first peak (k=0)
            
            if k == 0:
                tau =  peaks[k][0] - points[0][0]
            else:
                tau = peaks[k][0] - points[k-1][0]
            right = find_next_tau(points, i, tau)

            score = math.fabs(zscore.zscore_linear(peaks[k][1], points[left : right+1]))
            scores.append(score)

            # next left
            left = i
            k += 1
        else:
            scores.append(0)

    return np.array(scores)


def significant_zscore_peaks(points, peaks_idx, t=1.0):
    scores = zscore_peaks_values(points, peaks_idx)
    return scores > t


def significant_zscore_peaks_iso(points, peaks_idx):
    scores = zscore_peaks_values(points, peaks_idx)
    positive_scores = scores[scores > 0]
    t = thresholding.isodata(positive_scores)
    return scores > t


def mountaineer_peak_valley(points, threshold=1):

    possible_peak = possible_valley = False
    potential_peak_idx = potential_valley_idx = 0
    potential_peak_value = potential_valley_value = 0
    num_steps = 0

    peaks = np.full((len(points)), False)
    valley = np.full((len(points)), False)

    for i in range(1, len(points)):
        if points[i][1] > points[i-1][1]:
            num_steps += 1
            if not possible_valley:
                possible_valley = True
                potential_valley_idx = i-1
                potential_valley_value = points[i-1][1]
        else:
            if num_steps >= threshold:
                possible_peak = True
                potential_peak_idx = i-1
                potential_peak_value = points[i-1][1]
            else:
                if possible_valley:
                    if points[i][1] <= potential_valley_value:
                        potential_valley_idx = i
                        potential_valley_value = points[i][1]
                
                if possible_peak:
                    if points[i-1][1] > potential_valley_value:
                        potential_peak_idx = i-1
                        potential_peak_value = points[i-1][1]
                    else:
                        peaks[potential_peak_idx] = True
                    
                    if possible_valley:
                        valley[potential_peak_idx] = True
                        possible_valley = False
                    
                    threshold = int(0.6*num_steps)
                    possible_peak = False
            num_steps = 0
    return peaks, valley
