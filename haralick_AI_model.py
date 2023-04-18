
from sklearn.preprocessing import LabelEncoder
from skimage.feature import graycomatrix, graycoprops
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.ensemble import GradientBoostingClassifier
import torchvision.transforms as transforms
import os
import matplotlib.pyplot as plt
from skimage import img_as_float
from skimage.filters import threshold_otsu
from skimage.transform import resize
from skimage.color import rgb2gray
from skimage import util
from skimage import color
from skimage import filters
from skimage.color import rgb2lab, rgb2gray
from skimage.transform import resize
from sklearn.cluster import KMeans
import numpy as np
import pickle



import numpy as np


def predict_disease1(img):

      
      # Apply Otsu's thresholding to separate foreground and background
     

      img_gray = color.rgb2gray(img)
      thresh = filters.threshold_otsu(img_gray) 
      img_binary = img_gray > thresh 

      # Display the result
      #plt.imshow(img_binary, cmap='gray')
      #print('The label of this leaf is', random_file)

      # Invert the binary image to set background to white and foreground to black
      import numpy as np


      img_binary_inverted = np.logical_not(img_binary)

      # Replace the background with original colored pixels
      img_replaced = img.copy()
      img_replaced[img_binary_inverted] = img[img_binary_inverted]

      # Replace the foreground with white pixels
      img_replaced[img_binary] = [255, 255, 255]

      # Display the result
      #plt.imshow(img_replaced)
      #print('The label of this leaf is', random_file)

      # Create a mask to select only the non-white pixels
      nonwhite_mask = (img_replaced != [255, 255, 255]).all(axis=2)

      # Count the number of non-white pixels
      num_nonwhite_pixels = np.count_nonzero(nonwhite_mask)

      #print('The number of non-white pixels is', num_nonwhite_pixels)

      

      # Convert the image to HSV color space
      img_hsv = color.rgb2hsv(img_replaced)

      # Extract the brightness, hue, and saturation channels
      brightness = img_hsv[:,:,2]
      hue = img_hsv[:,:,0]
      saturation = img_hsv[:,:,1]


      # Normalize the grayscale image to be between 0 and 255
      img_gray_norm = (img_gray - np.min(img_gray)) * (255 / (np.max(img_gray) - np.min(img_gray)))

      # Create a binary image using Otsu's method
      # Only apply Otsu's method to non-white pixels
      thresh_val = threshold_otsu(img_gray_norm[img_gray_norm < 255])
      img_binary = (img_gray_norm >= thresh_val).astype('uint8') * 255


      # Apply mask to exclude white pixels from consideration
      img_binary_resized = resize(img_binary.astype(np.uint8),       
      (img_replaced.shape[0], img_replaced.shape[1]), 
      preserve_range=True).astype(np.uint8)
      img_replaced[img_binary_resized != 0] = 255
      mask = (brightness > 0.20) & (saturation > 0.20)
      img_nonwhite_hue = hue[mask]

      thresh = filters.threshold_otsu(img_nonwhite_hue)
      thresh_hue = np.mean(img_nonwhite_hue[img_nonwhite_hue < thresh])


      thresh = filters.threshold_otsu(img_nonwhite_hue) 
      thresh_hue = np.mean(img_nonwhite_hue[img_nonwhite_hue < thresh])

      # Replace the foreground with original colored pixels and apply brightness mask
      img_replaced = img_replaced.copy()
      mask_fg = (brightness > 0.05) & (hue <= thresh_hue)
      img_replaced[mask_fg] = img_replaced[mask_fg]

      # Replace the background with white pixels and apply brightness mask
      mask_bg = (brightness > 0.05) & (hue > thresh_hue)
      img_replaced[mask_bg] = [255, 255, 255]



      # Display the result
      #plt.imshow(img_replaced)
      #plt.title('Original colored pixels in the background and white pixels in the foreground')
      #plt.show()

      # Calculate the area of the colored pixels that were mapped
      num_diseased_pixels = np.count_nonzero(mask_fg)
      #print('The area of colored pixels is', num_diseased_pixels)

      # Create a mask for the original colored pixels
      mask_colored_pixels = np.any(img_replaced != [255, 255, 255], axis=-1)

      # Count the number of non-white pixels in the mask
      num_original_colored_pixels = np.count_nonzero(mask_colored_pixels)
      #print('The number of original colored pixels that were mapped is', num_original_colored_pixels)

      severity = num_original_colored_pixels/num_nonwhite_pixels;
      #print('This Plant have a severity of ', severity , ' or ', severity *100, '%');


      # Convert img_replaced to grayscale using CIELab colorspace
      img_lab = rgb2lab(img_replaced)
      img_gray = img_lab[:,:,0]

      # Rescale the pixel values of the grayscale image to the full range of intensity values
      img_gray = (img_gray - np.min(img_gray)) / (np.max(img_gray) - np.min(img_gray)) * 255

      # Create a mask to exclude white pixels from consideration
      img_binary_resized = resize(img_binary.astype(np.uint8), output_shape=(img_replaced.shape[0], img_replaced.shape[1]))
      mask_nonwhite =  (img_binary == 0)

      # Convert mask_nonwhite to a numpy array
      mask_nonwhite = np.array(mask_nonwhite, dtype=np.uint8)

      # Set white pixels in the grayscale image to white
      img_gray[np.logical_not(mask_nonwhite)] = 255

      img_gray = img_gray.astype(np.uint8)


      # Display the grayscale image
      #cv2_imshow(cv2.resize(img_gray, (img_gray.shape[1]//2, img_gray.shape[0]//2)))

      # Calculate Haralick texture features from non-white pixels
      distances = [1, 2,3]
      angles = [0, np.pi/4, np.pi/2 , 3*np.pi/4]

      haralick_feat = graycomatrix(img_gray, distances=distances, angles=angles, symmetric=True, normed=True)

      contrast = graycoprops(haralick_feat, 'contrast')
      dissimilarity = graycoprops(haralick_feat, 'dissimilarity')
      homogeneity = graycoprops(haralick_feat, 'homogeneity')
      energy = graycoprops(haralick_feat, 'energy')
      correlation = graycoprops(haralick_feat, 'correlation')

      # Display the Haralick texture feature statistics
      #print('label',label)
      #print('Contrast:', contrast)
      #print('Dissimilarity:', dissimilarity)
      #print('Homogeneity:', homogeneity)
      #print('Energy:', energy)
      #print('Correlation:', correlation)
      
    

      # Load the pre-trained GBM model from a saved file
      with open('76%haralick_.pkl', 'rb') as f:
          gbm = pickle.load(f)

      # Prepare the user features to be compared in the GBM model
      features = np.array([contrast, dissimilarity, homogeneity, energy, correlation])
      feature_list = features.ravel().tolist()

      # Use the pre-trained GBM model to predict the label of the user's features
      predicted_label = gbm.predict([feature_list])[0]

      class_mapping = {0:'Alternaria' , 1: 'Cercospora' , 2: 'EarlyBlight', 3:'LateBlight', 4: 'Virus'}
      predicted_class = class_mapping[predicted_label]

      # Print the predicted label
      #print('Predicted label:', predicted_label)

      return round(severity*100), predicted_class