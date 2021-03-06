# MDPH612_Project
DICOM reader for displaying multiple contours and webapp for patients to view their CT scan, browse their contoured organs and view side effects corresponding to each one.

### Requirements
`Python 3`

Packages: 
* numpy
* pydicom
* matplotlib
* Pillow
* psycopg2
* Flask
* dicom-contour


## pydicom_reader.py
My code uses direct and modified code from [dicom-contour](https://github.com/KeremTurgutlu/dicom-contour)

To use, first install package:
```
pip install dicom-contour
```
Code assumes that the CT slices and RTStruct are in the same folder, whose path is specified by the user. Any naming convention can be used assuming the file ends in `.dcm`.

For the code to work with DICOM files that aren't named by their SOPInstanceUID and to plot multiple contours at once with user-defined colours, the following functions should be replaced in the [contour.py file](https://github.com/KeremTurgutlu/dicom-contour/blob/master/dicom_contour/contour.py):
```
def coord2pixels(contour_dataset, path)
def get_data(path, index, ordered_slices = 0, contour_file = 0, img_path = 0)
```
These functions, along with new ones, are defined in [pydicom_reader.py](https://github.com/kaylaosullivan/MDPH612_Project/blob/master/pydicom_reader.py)

The function:
```
plot_all_contours(proi,colour_dict, pslice, path)
```

Will plot the CT slice `pslice` from DICOM files at `path` with and without contour indices `proi`, whose colours are defined in `colour_dict`.   


## webbapp.py
Code for webapp to allow patients to view their CT scans with and without contours and to select a contoured organ to view the potential side effects associated with it
Information about organs, image file locations and patient information is setup up in [patient_db.py](https://github.com/kaylaosullivan/MDPH612_Project/blob/master/webapp/patient_db.py).

The image file path of the slices with and without contours can be set in `patient_db.py`. However, within `webapp.py` it is assumed that the slices with individual contours are saved with the convention: `"p"+{patientID}+"_images/"+{organ name in database}+".png"`


