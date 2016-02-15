
settings001002 = {
    'use_roi': True,
    'rotation_script': "main_rotation_haarcascade_face_eyes.json",
    'detect_script': "main_haarcascade_face_size.json",
    'kodsettings': "mSURF/info001024.json",
    # 'kodsettings': "ORB/info001022.json",
    'knn': 2
}


def get_settings(algoID):
    """
    Return algorithm object by algorithm ID algoID.

    :param algoID: Unique algorithm identificator
        001     - Verification algorithms
        00101   - Clustering Matching Verification algorithm
                    without creating template
                001011 - ... based on openCV BRISK Features Detector
                001012 - ... based on openCV ORB Features Detector
                001013 - ... based on openCV SURF Features Detector
                001014 - ... based on mahotas SURF Features Detector
        00102   - Clustering Matching Verification algorithm
                    with creating L0-layer template
                001021 - ... based on openCV BRISK Features Detector
                001022 - ... based on openCV ORB Features Detector    (Default)
                001023 - ... based on openCV SURF Features Detector
                001024 - ... based on mahotas SURF Features Detector
        00103   - Clustering Matching Verification algorithm
                    with creating L1-layer template
                001031 - ... based on openCV BRISK Features Detector
                001032 - ... based on openCV ORB Features Detector
                001033 - ... based on openCV SURF Features Detector
                001034 - ... based on mahotas SURF Features Detector
        002     - Identification algorithms
    :return: Algorithm object instance
    """
    if algoID and len(algoID) == 6:
        algorithms = {"001011": settings001002,
                      "001012": settings001002,
                      "001013": settings001002,
                      "001014": settings001002,
                      "001021": settings001002,
                      "001022": settings001002,
                      "001023": settings001002,
                      "001024": settings001002,
                      "001031": settings001002,
                      "001032": settings001002,
                      "001033": settings001002,
                      "001034": settings001002
                      }
        if algorithms.keys().__contains__(algoID):
            return algorithms[algoID]
    return dict()


def get_attribute(algoID, name):
    settings = get_settings(algoID)
    return settings.get(name, None)
