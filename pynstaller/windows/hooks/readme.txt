pyinstaller --noconfirm --onefile --console --clean --collect-all "reportlab.graphics.barcode" `
--collect-all reportlab.graphics.barcode  --hidden-import=numpy --hidden-import=numpy.core._dtype_ctypes `
--hidden-import=numpy.core._methods --hidden-import=numpy.core._multiarray_umath --clean --additional-hooks-dir=./hooks `
--add-data "C:/Users/zitel/.ssh/Desktop/TEST/fit/asset;asset/" --add-data "C:/Users/zitel/.ssh/Desktop/TEST/fit/view;view/" `
--add-data "C:/Users/zitel/.ssh/Desktop/TEST/fit/controller;controller/" --add-data "C:/Users/zitel/.ssh/Desktop/TEST/fit/common;common/" `

--add-data "C:/Users/zitel/.ssh/Desktop/TEST/fit/model;model/" "C:/Users/zitel/.ssh/Desktop/TEST/fit/fit.py"


pyinstaller --noconfirm --onefile --console --clean --collect-all "reportlab.graphics.barcode" `
--collect-all reportlab.graphics.barcode  --hidden-import=numpy --hidden-import=numpy.core._dtype_ctypes `
--hidden-import=numpy.core._methods --hidden-import=numpy.core._multiarray_umath --clean --additional-hooks-dir=./hooks `
--add-data "./asset;asset/" --add-data "./view;view/" --add-data "./controller;controller/" --add-data "./common;common/" `
--add-data "./model;model/" "./fit.py"



pyinstaller --noconfirm --onefile --console --clean --collect-all "reportlab.graphics.barcode" `
--collect-all reportlab.graphics.barcode  --hidden-import=numpy --hidden-import=numpy.core._dtype_ctypes `
--hidden-import=numpy.core._methods --hidden-import=numpy.core._multiarray_umath --clean --additional-hooks-dir=./hooks `
--add-data "./asset;asset/" --paths "./view;view/" --paths "./controller;controller/" --paths "./common;common/" `
--paths "./model;model/" "./fit.py"


pyinstaller --noconfirm --onefile --console --clean --collect-all "reportlab.graphics.barcode" `
--hidden-import=numpy --hidden-import=numpy.core._dtype_ctypes `
--hidden-import=numpy.core._methods --hidden-import=numpy.core._multiarray_umath `
--hidden-import=view.configurations --hidden-import=controller.configurations --hidden-import=model.configurations `
--clean --additional-hooks-dir=./hooks fit.py


pyinstaller --noconfirm --onefile --console --clean --collect-all "reportlab.graphics.barcode" `
--collect-all reportlab.graphics.barcode  --hidden-import=numpy --hidden-import=numpy.core._dtype_ctypes `
--hidden-import=numpy.core._methods --hidden-import=numpy.core._multiarray_umath `
--clean --additional-hooks-dir=./hooks fit.py


pyinstaller --noconfirm --onefile --console --clean --collect-all "reportlab.graphics.barcode" `
--hidden-import=numpy.core._multiarray_umath `
--hidden-import=view.configurations --hidden-import=controller.configurations --hidden-import=model.configurations  `
--clean --additional-hooks-dir=./hooks fit.py


pyinstaller --noconfirm --onefile --console --clean `
>> --additional-hooks-dir=./installer/windows/hooks --icon=../icon.png --specpath=./installer/windows/ `
>> --distpath=./installer/windows/dist --workpath=./installer/windows/build `
>> fit.py