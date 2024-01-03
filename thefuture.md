SfM pipeline:
Goal: Collect pose and scene information from video footage

0. Calculate the intrinsic matrix of the camera
1. Calculate ORB / SIFT features (10 frames will do for now), and append to a list
2. (Implement V2) Add SAM aggregator to filter matches (check persistence features also)
3. Solve Lucas_kanarde problem (get camera pose and scene structure)
4. (Implement V3) Add bundle adjustment for pose estimate and scene reconstruction; only if absolutely necessary 


Assuming that assembling the E matrix with points across 5 frames

Need to create dict for a pseudo linked-list, pointing to the next match.