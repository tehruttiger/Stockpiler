python -m nuitka --standalone --follow-imports --enable-plugin=tk-inter --enable-plugin=numpy Stockpiler.py \
&& cp ./*.csv ./Stockpiler.dist \
&& cp ./Bmat.ico ./Stockpiler.dist \
&& cp -r ./CheckImages ./Stockpiler.dist \
&& cp -r ./UI ./Stockpiler.dist \
&& cp -r ./Compare ./Stockpiler.dist \
&& mkdir ./Stockpiler.dist/Stockpiles