#!/bin/bash

data_file_names=("genesis.txt" "actors.json") 

for name in "${data_file_names[@]}"; do
    echo $name
    cp $PWD/bootstrap/$name $PWD/app/utils/bootstrap_data/
done