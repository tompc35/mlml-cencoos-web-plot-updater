rm -rf mlml-shorestation-processing
git config --global user.email "thomas.p.connolly@sjsu.edu"
git config --global user.name "Tom Connolly"
git clone https://github.com/physoce/mlml-shorestation-processing.git
cp mlml_data_path.py mlml-shorestation-processing/msp/util/
cd mlml-shorestation-processing/msp/moss_landing/
python process_mlml_data.py
pwd
ls
cd ../../..
pwd
ls
ls Data/MLML_shore_stations/moss_landing/netcdf/

mkdir maintenance_log  
cp mlml-shorestation-processing/msp/moss_landing/maintenance_log/Seawater\ Maintenance\ Log\ -\ Sheet1.csv maintenance_log

python make_shore_station_figures.py
git pull origin main
git add figures/
git commit -m "automatically updated figures"
git push origin main