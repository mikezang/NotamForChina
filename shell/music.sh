pushd .
cd Python/scraping/scraping
python3 scraping.py --url www.xiami.com -l ~/Scripts/Python/logs -d ~/Music -s $1 -f $2 
popd
