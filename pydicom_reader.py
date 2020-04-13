import os
import pydicom
import numpy as np
import scipy
import csv
from pil import Image, ImageDraw
import matplotlib.pyplot as plt
from dicom_contour.contour import *

"""
Modified from https://github.com/KeremTurgutlu/dicom-contour/blob/master/dicom_contour/contour.py 
to read DICOM files with any naming convention (ie, no longer assumes SOAPInstanceIUD in file name)
"""
def coord2pixels(contour_dataset, path):
    """
    Given a contour dataset (a DICOM class) and path that has .dcm files of
    corresponding images. This function will return img_arr and contour_arr (2d image and contour pixels)
    Inputs
        contour_dataset: DICOM dataset class that is identified as (3006, 0016)  Contour Image Sequence
        path: string that tells the path of all DICOM images
    Return
        img_arr: 2d np.array of image with pixel intensities
        contour_arr: 2d np.array of contour with 0 and 1 labels
    """

    contour_coord = contour_dataset.ContourData
    # x, y, z coordinates of the contour in mm
    coord = []
    for i in range(0, len(contour_coord), 3):
        coord.append((contour_coord[i], contour_coord[i + 1], contour_coord[i + 2]))

    # extract the image id corresponding to given countour
    # read that dicom file
    img_ID = contour_dataset.ContourImageSequence[0].ReferencedSOPInstanceUID
    img_path = ""
    
    
    ###### MODIFIED SECTION #######
    if path[-1] != '/': path += '/'
    # get .dcm contour file
    
    fpaths = [path + f for f in os.listdir(path) if '.dcm' in f]
   
    # Search through each file to match contour sequence to image with correct SOPInstanceUID
    for fpath in fpaths:
        f = dicom.read_file(fpath)
        if f.SOPInstanceUID == img_ID:
            img_path = fpath  
            break            
       
    img = dicom.read_file(img_path)
    ###############################    
    
    img_arr = img.pixel_array

    # physical distance between the center of each pixel
    x_spacing, y_spacing = float(img.PixelSpacing[0]), float(img.PixelSpacing[1])

    # this is the center of the upper left voxel
    origin_x, origin_y, _ = img.ImagePositionPatient
 
    # y, x is how it's mapped
    pixel_coords = [(np.ceil((y - origin_y) / y_spacing), np.ceil((x - origin_x) / x_spacing)) for x, y, _ in coord]

    # get contour data for the image
    rows = []
    cols = []
    for i, j in list(set(pixel_coords)):
        rows.append(i)
        cols.append(j)
    contour_arr = csc_matrix((np.ones_like(rows), (rows, cols)), dtype=np.int8, shape=(img_arr.shape[0], img_arr.shape[1])).toarray()

    return img_arr, contour_arr, img_ID

"""
Modified from https://github.com/KeremTurgutlu/dicom-contour/blob/master/dicom_contour/contour.py 
to read DICOM files with any naming convention (ie, no longer assumes SOAPInstanceIUD in file name)
and to have the option to input the ordered slices, contour file and image path to improve efficiency
when plotting multiple contours at once.
"""
def get_data(path, index, ordered_slices = 0, contour_file = 0, img_path = 0):
    """
    Generate image array and contour array
    Inputs:
        path (str): path of the the directory that has DICOM files in it
        contour_dict (dict): dictionary created by get_contour_dict
        index (int): index of the desired ROISequence
        
        Optional:
            ordered_slices: ordered tuples of filename and z-position (obtained from slice_order function in contour.py)
            contour_file: name of the contour file
            img_path: put any DICOM file path if you only plan to look at slices where all of your input contours exist, if
                      you need all slices to be accurate, leave as 0 
                      (NEEDS WORK TO BE EFFICIENT)
    Returns:
        images and contours np.arrays
    """
    images = []
    contours = []
    # handle `/` missing
    if path[-1] != '/': path += '/'
    # get contour file
    if (contour_file == 0):
        contour_file = get_contour_file(path)
    # get slice orders
    if(ordered_slices == 0):
        ordered_slices = slice_order(path)
    # get contour dict
    contour_dict = get_contour_dict(contour_file, path, index)
    fpaths = [path + f for f in os.listdir(path) if '.dcm' in f]
    n = 0 
    for k,v in ordered_slices:
        
        #### MODIFIED #####
        if (img_path ==0):
            # Search through each file to match contour sequence to image with correct SOPInstanceUID
            for fpath in fpaths:
                f = dicom.read_file(fpath)
                if f.SOPInstanceUID == k:
                    img_path = fpath  
                    fpaths.remove(fpath)
                    break
                
        # get data from contour dict
        if k in contour_dict:
            images.append(contour_dict[k][0])
            contours.append(contour_dict[k][1])
           # print(n," ",contour_dict[k][1].max())
        # get data from dicom.read_file
        else:
            img_arr = dicom.read_file(img_path).pixel_array
            contour_arr = np.zeros_like(img_arr)
            images.append(img_arr)
            contours.append(contour_arr)
        n+=1
        ####################
    return np.array(images), np.array(contours)

"""
Function to get specified slice from images and array of all specified contours at same slice
"""
def get_slice(images, multi_contours, slicenum):
    '''
    Input:
        images: all slices of CT scan
        multi_contours: array of all contours specified at all slices
    Output: 
        Array of image pixels at specified slice
        Array of arrays of contours at specified slice
    '''
    image_arr = images[slicenum]
    contour_arr = []
    
    for i in range(len(multi_contours)):
        contour_arr.append(multi_contours[i][slicenum])    
    return image_arr, contour_arr


"""
Function to plot multiple specified contours on a given slice
"""
def plot2dcontour_multi(images, contours, colours, slicenum=1, figsize=(20, 20)):
    """
    Inputs
        images: image slices array with pixel intensities
        contours: multiple contour array with pixels of 1 and at all slices
        colours: array of colours corresponding to contours array
        slicenum: slice you want to generate
    """
    
    img_arr, contour_arr = get_slice(images, contours, slicenum)

    # Plot CT slices without contours
    plt.figure(figsize=figsize)
    plt.subplot(1, 2, 1)
    plt.imshow(img_arr, cmap='gray', interpolation='none')
    plt.subplot(1, 2, 2)
    plt.imshow(img_arr, cmap='gray', interpolation='none')
    
    # Plot contours
    for index in range(len(colours)):
        masked_contour_arr = np.ma.masked_where(contour_arr[index] == 0, contour_arr[index])
        # Create custom colour map for each contour
        cmap = colors.ListedColormap([colours[index]])
        bounds=[1]
        norm = colors.BoundaryNorm(bounds, cmap.N)
        # Plot
        plt.imshow(masked_contour_arr, cmap=cmap, interpolation='none', alpha=1, norm=norm)
        
    plt.show()


"""
Function to prepare data and call necessary functions to plot multiple contours on the same CT slice
"""    
def plot_all_contours(roi_indices, colour_dict, slicenum, path):
    '''
    Input:
        roi_indices: Indices of ROIs to plot (indices according to how they appear in "get_roi_names")
        colour_dict: dict mapping each ROI index to desired contour colour
        slicenum: desired slice number to display
        path: path to DICOM files
    '''
    # Get contour file and contour names
    contour_file = get_contour_file(path)
    contour_data = dicom.read_file(path + '/' + contour_file)
    roi_names = get_roi_names(contour_data)
    
    all_contours = []
    colours = []
    
    # get slice orders
    ordered_slices = slice_order(path)
    
    # make into dict in future
#    fpaths = [path + f for f in os.listdir(path) if '.dcm' in f]
#    for k,v in ordered_slices:
#        for fpath in fpaths:
#            f = dicom.read_file(fpath)
#            if f.SOPInstanceUID == k:
#                img_path = fpath  
#                fpaths.remove(fpath)
#                #print(img_path)
#                break
    
    # Retrieve image and contour pixel data
    for index in roi_indices:
        print("Index ",index,": ",roi_names[index])
        
        images, contours = get_data(path, index=index, ordered_slices=ordered_slices, contour_file=contour_file,img_path='./SAMPLE_DICOM/CT/000213.dcm')
        all_contours.append(contours)
        colours.append(colour_dict[index])

    # generate plots
    plot2dcontour_multi(images,all_contours,colours,slicenum)



"""
Function to plot multiple specified contours individually on a given slice
"""
def plot_individual_contours(roi_indices, colour_dict, slicenum, path):
    '''
    Input:
        roi_indices: Indices of ROIs to plot (indices according to how they appear in "get_roi_names")
        colour_dict: dict mapping each ROI index to desired contour colour
        slicenum: desired slice number to display
        path: path to DICOM files
    '''
    for roi in roi_indices:
        plot_all_contours([roi], colour_dict, slicenum, path)
        
        

def main():
    # relevant paths
    RT_dose_path = './SAMPLE_DICOM/RTdose'
    RT_struct_path = './SAMPLE_DICOM/RTstruct'
    CT_files_path = './SAMPLE_DICOM/CT/'
    
    # Get DICOM file and show ROI names available
    path = CT_files_path
    contour_file = get_contour_file(path)
    contour_data = dicom.read_file(path + '/' + contour_file)
    roi_names = get_roi_names(contour_data)
    print("ROI Names: ", roi_names)

    # Dictionary mapping colours to ROI indices
    colour_dict = {
           6: 'lime',
           7: 'yellow',
           10:'red',
           11: 'cyan',
           13: 'red',
           16: 'green',
           18: 'pink',
           19: 'coral',
           21: 'fuchsia',
           22: 'orange',
           23: 'orange',
           24: 'blue',
           25: 'blue',
           26: 'blueviolet'
    }
   
    
    # Patient slices and contours to generate
    patient = 3
    
    if (patient == 1):
        pslice = 208
        proi = [6,7,21,22,23,24,25]
       
    if patient == 2:
        pslice = 179
        proi = [6,7,10,13,16,18,19,26]

    if patient == 3: 
        pslice = 115 
        proi = [6,11,19]
    
    if patient == 4:
        pslice = 150
        proi = [6,10,13,18,19,26]
        
 
    plot_all_contours(proi,colour_dict, pslice, path)
    #plot_individual_contours(proi,colour_dict, pslice, path)
    


if __name__ == "__main__":
   main()