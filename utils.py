import os
import cv2
import glob
from typing import List, Tuple
from matplotlib.pyplot import angle_spectrum
import matplotlib.pyplot as plt
import numpy as np
import random
from typing import Sequence, List, Optional
from skimage.metrics import structural_similarity



def get_data(path_A: str, path_B: str):
    img_data = []
    all_keypoints = []
    all_descriptors = []

    sift = cv2.SIFT_create()

    # Calculate Sift Features for Image A
    image = cv2.imread(path_A)
    img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    keypoints, descriptors = sift.detectAndCompute(gray, None)
    if img is None:
        keypoints = []
        descriptors = []
    else:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        keypoints, descriptors = sift.detectAndCompute(gray, None)

    img_data.append(img)
    all_keypoints.append(keypoints)
    all_descriptors.append(np.vstack(np.float32(descriptors)))

    # Calculate Sift Features for Image B
    image = cv2.imread(path_B)
    img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    if img is None:
        keypoints = []
        descriptors = []
    else:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        keypoints, descriptors = sift.detectAndCompute(gray, None)

    img_data.append(img)
    all_keypoints.append(keypoints)
    all_descriptors.append(np.vstack(np.float32(descriptors)))


    # img_data : list of images
    # all_keypoints : list of keypoints ([number_of_images x number_of_keypoints] - KeyPoint)
    # all_descriptors : list of descriptors ([number_of_images x num_of_keypoints, 128] - float)
    return img_data, all_keypoints, all_descriptors


def plot_keypoints(image: np.ndarray, keypoints: List[cv2.KeyPoint], ImageID: str = None):
    fig, ax = plt.subplots()
    image = cv2.drawKeypoints(image, keypoints, None,
                              flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
    # ax.imshow(image)

    if ImageID is not None:
        fig.suptitle(ImageID)
        plt.savefig('images/Top100/out/'+ImageID)

    # Show the image
    # plt.show()
    plt.close(fig)
    return image


def plot_matches(img1: np.ndarray, img2: np.ndarray, kp1: List[cv2.KeyPoint], kp2: List[cv2.KeyPoint], matches: List[cv2.DMatch], ImageID: str = None):
    fig, (ax1) = plt.subplots(1, 1)
    result = cv2.drawMatchesKnn(img1, kp1, img2, kp2, [
                                [m] for m in matches], None)
    # ax1.imshow(result)

    if ImageID is not None:
        fig.suptitle(ImageID)
        # plt.savefig('images/Top100/out/'+ImageID)

    # Show the image
    #plt.show()
    plt.close(fig)
    return result


def plot_transformed_image(img1: np.ndarray, img2: np.ndarray, ImageID: str = None):
    added_image = cv2.addWeighted(img1, 1, img2, 0.7, 0.3)

    fig, (ax) = plt.subplots()
    # ax.imshow(added_image)

    
    if ImageID is not None:
        fig.suptitle(ImageID)
        # plt.savefig('images/Top100/out/'+ImageID)
    
    # plt.show()
    return added_image


def calculate_matches(des1: np.ndarray, des2: np.ndarray) -> List[int]:

    bf = cv2.BFMatcher()
    matches = bf.knnMatch(des1, des2, k=2)

    # LOWE ratio test
    result = []
    for m, n in matches:
        if (m.distance/n.distance) < 0.8:
            result.append(m)

    # result : indices of keypoints (kp1 (col1) and kp2 (col2)) per match ([num_of_matches x 2] - int)
    return result


def get_geometric_transform(p1, p2):
    num_points = len(p1)
    A = np.zeros((2*num_points, 9))
    for p in range(num_points):
        first = np.array([p1[p, 0], p1[p, 1], 1])
        A[2*p] = np.concatenate(([0, 0, 0], -first, p2[p, 1]*first))
        A[2*p + 1] = np.concatenate((first, [0, 0, 0], -p2[p, 0]*first))
    U, D, V = np.linalg.svd(A)
    H = V[8].reshape(3, 3)

    # homography from p1 to p2
    return (H / H[-1, -1]).astype(np.float32)


def get_transform(kp1: List[cv2.KeyPoint], kp2: List[cv2.KeyPoint], matches: List[cv2.DMatch]) -> Tuple[np.ndarray, List[int]]:

    kp1_match = np.float32([kp1[m.queryIdx].pt for m in matches])
    kp2_match = np.float32([kp2[m.trainIdx].pt for m in matches])

    inliers = []
    thres = 5
    n = 1000

    for i in range(n):
        # choose 4 random matches and calc the transformation based on these samples
        if len(matches) <= 4:
            trans = None
            inliers = None
            return trans, inliers
        idx = random.sample(range(len(matches)), 4)
        s1 = kp1_match[idx, :]
        s2 = kp2_match[idx, :]
        trans = get_geometric_transform(s1, s2)

        transformed_kp1 = cv2.perspectiveTransform(np.array([kp1_match]), trans)
        transformed_kp1 = transformed_kp1[0, :, :]

        dist = np.linalg.norm(transformed_kp1-kp2_match, axis=1)
        inds = np.argwhere(dist < thres)

        if (len(inds) > len(inliers)):
            inliers = np.asarray(inds)

    s1 = kp1_match[inliers, [0, 1]]
    s2 = kp2_match[inliers, [0, 1]]
    trans = get_geometric_transform(s1, s2)


    # trans : homographies from left (kp1) to right (kp2) image ([3 x 3] - float)
    # inliers : list of indices, inliers in 'matches' ([number_of_inliers x 1] - int)
    return trans, inliers

def create_pdf_report_from_images(
    img_vis_kp_A: Optional[np.ndarray],
    img_vis_kp_B: Optional[np.ndarray],
    img_vis_matches: Optional[np.ndarray],
    img_vis_inliers: Optional[np.ndarray],
    img_vis_overlay: Optional[np.ndarray],
    output_pdf_path: str
):

    # print(f"  Attempting to create PDF: {os.path.basename(output_pdf_path)}")
    fig = None

    images_to_plot = [img_vis_kp_A, img_vis_kp_B, img_vis_matches, img_vis_inliers, img_vis_overlay]
    image_names = ["Keypoints A", "Keypoints B", "Matches", "Inliers", "Overlay"] # For error messages

    # --- Basic Input Validation ---
    valid_inputs = True
    for i, img in enumerate(images_to_plot):
        if not isinstance(img, np.ndarray):
            # print(f"  Error: Input '{image_names[i]}' is not a NumPy array (Type: {type(img)}). Cannot create PDF.")
            valid_inputs = False
    if not valid_inputs:
        return

    try:
        # --- Create Figure and Axes (3 rows, 2 columns) ---
        fig, axes = plt.subplots(3, 2, figsize=(12, 18)) # e.g., taller if matches images are wide
        axes_flat = axes.ravel() # Flatten axes array for easier indexing

        # --- Plot the 5 images ---
        for i, img_bgr in enumerate(images_to_plot):
            # Input type already checked
            # Check image dimensions (color vs grayscale)
            img_display = img_bgr
            try:
                if len(img_bgr.shape) == 2: # Grayscale
                    cmap = 'gray'
                elif len(img_bgr.shape) == 3 and img_bgr.shape[2] == 3: # Color BGR
                    # Convert BGR to RGB for Matplotlib
                    # img_display = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
                    cmap = None # Use default RGB colormap
                else:
                    # print(f"  Error: Unexpected shape for image '{image_names[i]}': {img_bgr.shape}. Plotting placeholder.")
                    # Create a black placeholder with error text
                    h_ref, w_ref = (200, 200) # Default placeholder size
                    img_display = np.zeros((h_ref, w_ref, 3), dtype=np.uint8)
                    cv2.putText(img_display, f"Invalid Input '{image_names[i]}'", (10, h_ref // 2),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
                    # img_display = cv2.cvtColor(img_display, cv2.COLOR_BGR2RGB) # Convert placeholder to RGB
                    cmap = None

                axes_flat[i].imshow(img_display, cmap=cmap)

            except Exception as img_err:
                 # print(f"  Error processing/plotting image '{image_names[i]}': {img_err}")
                 # Plot placeholder on error
                 h_ref, w_ref = (200, 200)
                 img_display = np.zeros((h_ref, w_ref, 3), dtype=np.uint8)
                 cv2.putText(img_display, f"Plot Error '{image_names[i]}'", (10, h_ref // 2),
                             cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
                 axes_flat[i].imshow(cv2.cvtColor(img_display, cv2.COLOR_BGR2RGB))

            axes_flat[i].axis('off')

        axes_flat[5].axis('off')

        # --- Adjust Layout and Save ---
        plt.tight_layout(pad=0.5)

        output_dir = os.path.dirname(output_pdf_path)
        if output_dir and not os.path.exists(output_dir):
             # print(f"  Creating output directory: {output_dir}")
             os.makedirs(output_dir, exist_ok=True)

        plt.savefig(output_pdf_path, format='pdf', bbox_inches='tight', pad_inches=0.1, dpi=150)
        # print(f"  Successfully saved PDF (images only) to: {output_pdf_path}")

    except Exception as e:
        print(f"!! Error during PDF generation or saving process: {e}")
    finally:
        # IMPORTANT: Close the plot figure to release memory
        if fig is not None and plt.fignum_exists(fig.number):
              plt.close(fig)
              # print(f"  Plot figure closed for {os.path.basename(output_pdf_path)}.")
    plt.close(fig)


def orb_sim(img1, img2):
    orb = cv2.ORB_create()

    kp_a, desc_a = orb.detectAndCompute(img1, None)
    kp_b, desc_b = orb.detectAndCompute(img2, None)

    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

    matches = bf.match(desc_a, desc_b)
    similar_regions = [i for i in matches if i.distance < 50]
    good_matches = similar_regions
    """
    if len(matches) == 0:
        return 0
    else:
        similarity_score = len(similar_regions) / len(matches)
    match_img = cv2.drawMatches(img1, kp_a, img2, kp_b, good_matches, None, matchColor=(0, 255, 0), singlePointColor=(0, 0, 255), flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)
    plt.figure(figsize=(16, 8))
    plt.imshow(cv2.cvtColor(match_img, cv2.COLOR_BGR2RGB))
    plt.title(f'ORB Good Matches (Count: {len(good_matches)} / Total Matched: {len(matches)}) - Similarity: {similarity_score:.2f}')
    plt.axis('off') # Hide axes
    plt.show()
    """
    if len(matches) == 0:
        return 0
    return len(similar_regions) / len(matches)


def structural_sim(img1, img2):
    sim, diff = structural_similarity(img1, img2, full=True)
    return sim