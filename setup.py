# setup.py
from distutils.core import setup
import glob
import py2exe
 

setup(name="emblem",
      windows=[
               {
                   "script":"main.py",
                   "icon_resources": [(1, "icon.ico")],
				   "packages": ['pygame.mixer'],
				   "bundle_files": 0
               }
              ],
      data_files=[
			  ("image", glob.glob("image\\*.png")),
      			  ("image", glob.glob("image\\*.jpg")),
      			  ("music", glob.glob("music\\*.ogg")),
      			  ("sound", glob.glob("sound\\*.*")),
      			  ("data", glob.glob("data\\*.*")),
      			  ("font\\ipag", glob.glob("font\\ipag\\*")),
                  ],
)
