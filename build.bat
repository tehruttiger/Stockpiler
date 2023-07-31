py -m nuitka --standalone --follow-imports --enable-plugin=tk-inter --enable-plugin=numpy Stockpiler.py && (
    copy .\*.csv .\Stockpiler.dist
    copy .\Bmat.ico .\Stockpiler.dist
    xcopy /E /I .\CheckImages .\Stockpiler.dist\CheckImages
    xcopy /E /I .\UI .\Stockpiler.dist\UI
    if not exist .\Stockpiler.dist\Stockpiles mkdir .\Stockpiler.dist\Stockpiles
)
