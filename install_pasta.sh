#! /bin/bash
#################################################################################
#     File Name           :     install_pasta.sh
#     Created By          :     qing
#     Creation Date       :     [2017-04-20 06:26]
#     Last Modified       :     [2017-04-20 06:27]
#     Description         :      
#################################################################################
git clone https://github.com/smirarab/pasta
git clone https://github.com/smirarab/sate-tools-linux
cd pasta
python setup.py develop --user


