rm -rf mlml-shorestation-processing
git clone -b web-update https://github.com/physoce/mlml-shorestation-processing.git
cp mlml_data_path.py mlml-shorestation-processing/msp/util/
cd mlml-shorestation-processing/msp/moss_landing/
python process_mlml_data.py
cd ../../../
# mkdir maintenance_log  
# cp mlml-shorestation-processing/msp/moss_landing/maintenance_log/Seawater\ Maintenance\ Log\ -\ Sheet1.csv maintenance_log
python make_shore_station_figures.py
