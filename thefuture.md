SfM pipeline:
Goal: Collect pose and scene information from video footage

0. Calculate the intrinsic matrix of the camera
1. Calculate ORB / SIFT features (10 frames will do for now), and append to a list
2. (Implement V2) Add SAM aggregator to filter matches (check persistence features also)
3. Monocular scene reconstruction (get camera pose and scene structure)
 - https://opencv24-python-tutorials.readthedocs.io/en/latest/py_tutorials/py_calib3d/py_epipolar_geometry/py_epipolar_geometry.html#epipolar-geometry -- Epipolar scene reconstruction. 

 https://github.com/PacktPublishing/OpenCV-with-Python-By-Example/blob/master/Chapter11/stereo_match.py 
 
4. Bundle adjustment 


Need to create dict for a pseudo linked-list, pointing to the next match.