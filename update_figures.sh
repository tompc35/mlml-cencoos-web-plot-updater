rm -rf mlml-shorestation-processing
git clone https://github.com/physoce/mlml-shorestation-processing.git
cp mlml_data_path.py mlml-shorestation-processing/msp/util/
cd mlml-shorestation-processing/msp/moss_landing/
python process_mlml_data.py
pwd
ls
cd ../../..
pwd
ls
ls Data/MLML_shore_stations/moss_landing/
python make_shore_station_figures.py
git pull origin main
git add figures/
git commit -m "automatically updated figures"
git push origin main