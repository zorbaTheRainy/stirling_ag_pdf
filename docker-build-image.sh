#!/bin/bash
# set -x 

read -p "Enter the Docker Image's tag: " IMAGE_TAG
echo
read -n1 -s -r -p "Do you wish to push the image to Docker Hub? [Y/n]: " reply
if [ "$reply" = "" ]; then reply="Y"; fi
case $reply in
    [Yy]* )
        doPush=1 # True
        ;;
    * ) 
        doPush=0 # False
        ;;
esac
echo

export IMAGE_TAG
export IMAGE_NAME="zorbatherainy/stirling_ag_pdf"
if [ $doPush -eq 1 ]
then
    echo push
    docker buildx build --platform=amd64,arm64 --build-arg="IMAGE_TAG=${IMAGE_TAG}" --push -t ${IMAGE_NAME} -t ${IMAGE_NAME}:${IMAGE_TAG} .
else
    echo no
    docker buildx build --platform=amd64,arm64 --build-arg="IMAGE_TAG=${IMAGE_TAG}" -t ${IMAGE_NAME}:${IMAGE_TAG} .
fi

