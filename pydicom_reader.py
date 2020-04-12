#pydicom
import os
import pydicom
#from pydicom.filereader import read_dicomdir
import numpy as np
import scipy
# import cv2
import csv
from pil import Image, ImageDraw
#import dicom
import matplotlib.pyplot as plt

from dicom_contour.contour import *

def get_contour_file(path):
    """
    Get contour file from a given path by searching for ROIContourSequence 
    inside dicom data structure.
    More information on ROIContourSequence available here:
    http://dicom.nema.org/medical/dicom/2016c/output/chtml/part03/sect_C.8.8.6.html
    
    Inputs:
            path (str): path of the the directory that has DICOM files in it, e.g. folder of a single patient
    Return:
        contour_file (str): name of the file with the contour
    """
    # handle `/` missing
    if path[-1] != '/': path += '/'
    # get .dcm contour file
    fpaths = [path + f for f in os.listdir(path) if '.dcm' in f]
    n = 0
    #contour_file = 0
    
    for fpath in fpaths:
        f = dicom.read_file(fpath)
        if 'ROIContourSequence' in dir(f):
            contour_file = fpath.split('/')[-1]
            n += 1
        
    if n > 1: warnings.warn("There are multiple files, returning the last one!")
    print(contour_file)
    return contour_file

def cfile2pixels(file, path, ROIContourSeq=0):
    """
    Given a contour file and path of related images return pixel arrays for contours
    and their corresponding images.
    Inputs
        file: filename of contour
        path: path that has contour and image files
        ROIContourSeq: tells which sequence of contouring to use default 0 (RTV)
    Return
        contour_iamge_arrays: A list which have pairs of img_arr and contour_arr for a given contour file
    """
    # handle `/` missing
    if path[-1] != '/': path += '/'
    f = dicom.read_file(path + file)
    # index 0 means that we are getting RTV information
    RTV = f.ROIContourSequence[ROIContourSeq]
    # get contour datasets in a list
    contours = [contour for contour in RTV.ContourSequence]
    img_contour_arrays = [coord2pixels(cdata, path) for cdata in contours]
    return img_contour_arrays



def get_rt_structure(RT_struct_path):
    files = [os.path.join(RT_struct_path, f) for f in os.listdir(RT_struct_path)]
    if len(files) == 1:
        RT_struct_file = files[0]
    else:
        print('Error')
    ds = pydicom.read_file(RT_struct_file)
    print(ds.Modality)
    print (dir(ds))
    print("----------------------------------")
    dose_refs = []
    dose_ref = ds.StructureSetROISequence
    print(dir(dose_ref[0]))
    print(dose_ref[0].ROIName)
    for dose in dose_ref:
        # print dose.dir()
        if 'DoseReferencePointCoordinates' in dose.dir():
            dose_refs.append(dose.ROIName)
    # print '------>', dose_refs
    return dose_refs


def slice_order(path):
    """
    Takes path of directory that has the DICOM images and returns
    a ordered list that has ordered filenames
    Inputs
        path: path that has .dcm images
    Returns
        ordered_slices: ordered tuples of filename and z-position
    """
    # handle `/` missing
    if path[-1] != '/': path += '/'
    slices = []
    for s in os.listdir(path):
        try:
            f = dicom.read_file(path + '/' + s)
            f.pixel_array  # to ensure not to read contour file
            slices.append(f)
        except:
            continue

    slice_dict = {s.SOPInstanceUID: s.ImagePositionPatient[-1] for s in slices}
    ordered_slices = sorted(slice_dict.items(), key=operator.itemgetter(1))
    return ordered_slices

#def get_data(path, index):
#    """
#    Generate image array and contour array
#    Inputs:
#        path (str): path of the the directory that has DICOM files in it
#        contour_dict (dict): dictionary created by get_contour_dict
#        index (int): index of the desired ROISequence
#    Returns:
#        images and contours np.arrays
#    """
#    images = []
#    contours = []
#    # handle `/` missing
#    if path[-1] != '/': path += '/'
#    # get contour file
#    contour_file = get_contour_file(path)
#    # get slice orders
#    ordered_slices = slice_order(path)
#    # get contour dict
#    contour_dict = get_contour_dict(contour_file, path, index)
#    fpaths = [path + f for f in os.listdir(path) if '.dcm' in f]
#    n = 0 
#    for k,v in ordered_slices:
#        
#        for fpath in fpaths:
#            f = dicom.read_file(fpath)
#            if f.SOPInstanceUID == k:
#                img_path = fpath  
#                fpaths.remove(fpath)
#                break
#                
#        
#        # get data from contour dict
#        if k in contour_dict:
#            images.append(contour_dict[k][0])
#            contours.append(contour_dict[k][1])
#           # print(n," ",contour_dict[k][1].max())
#        # get data from dicom.read_file
#        else:
#            #img_arr = dicom.read_file(path + k + '.dcm').pixel_array
#            img_arr = dicom.read_file(img_path).pixel_array
#            contour_arr = np.zeros_like(img_arr)
#            images.append(img_arr)
#            contours.append(contour_arr)
#        n+=1
#    return np.array(images), np.array(contours)


def convert_dose(RT_dose_path):
    files = [os.path.join(RT_dose_path, f) for f in os.listdir(RT_dose_path)]
    if len(files) == 1:
        RT_dose_file = files[0]
    else:
        print('Error')
    ds = pydicom.read_file(RT_dose_file)
    # print ds.dir()
    dose_pixel = ds.pixel_array
    # print len(ds.PixelData)
    # print dose_pixel.shape

    rows = ds.Rows
    columns = ds.Columns
    pixel_spacing = ds.PixelSpacing
    image_position = ds.ImagePositionPatient
    # print 'DS', image_position
    x = np.arange(columns)*pixel_spacing[0] + image_position[0]
    y = np.arange(rows)*pixel_spacing[1] + image_position[1]
    z = np.array(ds.GridFrameOffsetVector) + image_position[2]
    beam_center = (np.argmin(abs(x)),np.argmin(abs(y)),np.argmin(abs(z)))
    return dose_pixel, x,y,z, pixel_spacing

def get_cts(CT_files_path):
    CT_files = [os.path.join(CT_files_path, f) for f in os.listdir(CT_files_path)]
    slices = {}
    for ct_file in CT_files:
        ds = pydicom.read_file(ct_file)

        # Check to see if it is an image file.
        # print ds.SOPClassUID
        if ds.SOPClassUID == '1.2.840.10008.5.1.4.1.1.2':
            #
            # Add the image to the slices dictionary based on its z coordinate position.
            #
            slices[ds.ImagePositionPatient[2]] = ds.pixel_array
        else:
            pass

    # The ImagePositionPatient tag gives you the x,y,z coordinates of the center of
    # the first pixel. The slices are randomly accessed so we don't know which one
    # we have after looping through the CT slice so we will set the z position after
    # sorting the z coordinates below.
    image_position = ds.ImagePositionPatient
    # print 'CT', image_position
    # Construct the z coordinate array from the image index.
    z = slices.keys()
    z = sorted(z)
    ct_z = np.array(z)

    image_position[2] = ct_z[0]

    # The pixel spacing or planar resolution in the x and y directions.
    ct_pixel_spacing = ds.PixelSpacing

    # Verify z dimension spacing
    b = ct_z[1:] - ct_z[0:-1]
    # z_spacing = 2.5 # Typical spacing for our institution
    if b.min() == b.max():
         z_spacing = b.max()
    else:
        print ('Error z spacing in not uniform')
        z_spacing = 0

    # print z_spacing

    # Append z spacing so you have x,y,z spacing for the array.
    ct_pixel_spacing.append(z_spacing)

    # Build the z ordered 3D CT dataset array.
    ct_array = np.array([slices[i] for i in z])

    print(ct_array.shape)    
    # plt.imshow(ct_array[50,:,:], origin='lower')
    plt.imshow(ct_array[:,255,:], origin='lower')
    # plt.imshow(ct_array[:,:,255], origin='lower')
    plt.show()
    # Now construct the coordinate arrays
    # print ct_pixel_spacing, image_position
    x = np.arange(ct_array.shape[2])*ct_pixel_spacing[0] + image_position[0]
    y = np.arange(ct_array.shape[1])*ct_pixel_spacing[1] + image_position[1]
    z = np.arange(ct_array.shape[0])*z_spacing + image_position[2]
    # print x
    # print image_position[0], image_position[1], image_position[2]
    # print ct_pixel_spacing[0], ct_pixel_spacing[1], ct_pixel_spacing[2]
    # print x, y
    # print (len(x), len(y))
    # # The coordinate of the first pixel in the numpy array for the ct is then  (x[0], y[0], z[0])
    return ct_array, x,y,z, ct_pixel_spacing

#def initialize(path):
#    contour_file = get_contour_file(path)
#    ordered_slices = slice_order(path)
#    return ordered_slices, contour
    
def plot_all_contours(roi_indices, colour_dict, slicenum, path):
    contour_file = get_contour_file(path)
    contour_data = dicom.read_file(path + '/' + contour_file)
    roi_names = get_roi_names(contour_data)
    
    all_contours = []
    colours = []
    #isFirst = True
    
    contour_file = get_contour_file(path)
    # get slice orders
    ordered_slices = slice_order(path)
    
    fpaths = [path + f for f in os.listdir(path) if '.dcm' in f]
    for k,v in ordered_slices:
        for fpath in fpaths:
            f = dicom.read_file(fpath)
            if f.SOPInstanceUID == k:
                img_path = fpath  
                fpaths.remove(fpath)
                break
    
    for index in roi_indices:
        print("Index ",index,": ",roi_names[index])
     
        images, contours = get_data(path, index=index, ordered_slices=ordered_slices, contour_file=contour_file,img_path=img_path)
        all_contours.append(contours)
        colours.append(colour_dict[index])
        #isFirst = False
    print(len(images))
    print(len(images[0]))
    print(images)
    print(images[0])
    print(images[0][0])
    #print(len)
    plot2dcontour_multi(images,all_contours,colours,slicenum)

def plot_individual_contours(roi_indices, colour_dict, slicenum, path):
    for roi in roi_indices:
        plot_all_contours([roi], colour_dict, slicenum, path)
        
        

def main():
    RT_dose_path = './SAMPLE_DICOM/RTdose'
    RT_struct_path = './SAMPLE_DICOM/RTstruct'
    CT_files_path = './SAMPLE_DICOM/CT/'
    #path = './SAMPLE_DICOM/CT/000005.dcm'
#    get_cts(CT_files_path)
#    get_cts('./example/ct0.dcm')
    # print(convert_dose(RT_dose_path))
    # get_rt_structure(RT_struct_path)
    
    path = CT_files_path
#    contour_file = get_contour_file(path)
#    contour_data = dicom.read_file(path + '/' + contour_file)
#    roi_names = get_roi_names(contour_data)
#    print("ROI Names: ", roi_names)

    # ordered files
#    ordered_slices = slice_order(path)
    
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
   
    patient = 1
    
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
        

    #plot_all_contours(proi,colour_dict, pslice, path)
    plot_individual_contours(proi,colour_dict, pslice, path)
    

#    for index in indices:
#        
#        print("Index ",index,": ",roi_names[index])
#        images, contours = get_data(path, index=index)
    
    # Get contour locations
#    indices = [24,25]
#    colours = ['red','cyan']
#    all_contours = []
#
#
##    
#    for index in indices:
#        
#        print("Index ",index,": ",roi_names[index])
#        images, contours = get_data(path, index=index)
#        all_contours.append(contours)
#    plot2dcontour_multi(images,all_contours,colours,208)
#        
    
#    
   # for img_arr, contour_arr in zip(images[207:208], contours[0][0][207:208]):
#        #plot2dcontour(img_arr, contour_arr)
#        plot2dcontour_multi(img_arr,all_contours,colours)
###   
if __name__ == "__main__":
   main()