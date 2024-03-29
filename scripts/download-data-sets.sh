#!/bin/bash

# Check if exactly 4 arguments are provided
if [ "$#" -ne 4 ]; then
    echo "Usage: $0 MIN_SF MAX_SF LAYOUT_TYPE SAVE_PATH"
    echo "MIN_SF: Minimum scale factor to download (one of 0.1, 0.3, 1, 3, 10, 30, 100, 300, 1000)"
    echo "MAX_SF: Maximum scale factor to download (same options as MIN_SF)"
    echo "LAYOUT_TYPE: 'graph' for projected layout, any other value for merged layout"
    echo "SAVE_PATH: The directory path where the files should be saved"
    exit 1
fi

MIN_SF=$1
MAX_SF=$2
LAYOUT_TYPE=$3
SAVE_PATH=$4

# Validate scale factors
ALLOWED_SFS="0.1 0.3 1 3 10 30 100 300 1000"
validate_sf() {
    for VALID_SF in $ALLOWED_SFS; do
        if [[ "$1" == "$VALID_SF" ]]; then
            return 0
        fi
    done
    echo "Error: Scale factor $1 is not valid. Must be one of $ALLOWED_SFS."
    exit 1
}

validate_sf $MIN_SF
validate_sf $MAX_SF

# Ensure SAVE_PATH exists
mkdir -p "$SAVE_PATH"
cd "$SAVE_PATH"

# Determine URL path based on LAYOUT_TYPE
if [ "$LAYOUT_TYPE" == "graph" ]; then
    URL_PATH="lsqb-projected"
    LAYOUT="projected"
else
    URL_PATH="lsqb-merged"
    LAYOUT="merged"
fi

# Function to download and unzip datasets for given scale factors
download_and_unzip_datasets() {
    local start_download=false
    for SF in $ALLOWED_SFS; do
        if [[ "$SF" == "$MIN_SF" ]]; then
            start_download=true
        fi
        if [[ "$start_download" = true ]] && [[ $(echo "$SF <= $MAX_SF" | bc -l) -eq 1 ]]; then
            FILE_NAME="social-network-sf${SF}-${LAYOUT}-fk.tar.zst"
            URL="https://repository.surfsara.nl/datasets/cwi/lsqb/files/${URL_PATH}/${FILE_NAME}"
            echo "Downloading scale factor ${SF} from ${URL}"
            # Download file
            curl --silent --fail "${URL}" --output "${FILE_NAME}"
            # Unzip the downloaded file
            echo "Unzipping ${FILE_NAME}"
            tar -xv --use-compress-program=unzstd -f "${FILE_NAME}"
            # Optionally, remove the compressed file after unzipping
            echo "Removing compressed file ${FILE_NAME}"
            rm "${FILE_NAME}"
        fi
        if [[ "$SF" == "$MAX_SF" ]]; then
            break
        fi
    done
}

download_and_unzip_datasets
