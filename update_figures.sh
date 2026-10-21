rm -rf mlml-shorestation-processing
git clone https://github.com/physoce/mlml-shorestation-processing.git
cp mlml_data_path.py mlml-shorestation-processing/msp/util/
cd mlml-shorestation-processing/msp/moss_landing/
python process_mlml_data.py
cd ../../..
python make_shore_station_figures.py