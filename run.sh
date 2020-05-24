#!/bin/bash
docker run -v /Users/tim/Downloads/takim/project/taki3/Melissa_stuff/andy_solomon_2019-12-09/UVMdata/MSc:/base:ro -v $(pwd)/test:/output \
    pennsive/bids-converter create -p "/base/x{subject}/processing_2020-03-04/{modality}.nii.gz" -ss 01
