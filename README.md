# Half as Fast website

A simple static website for displaying attempts to complete routes half as fast as the record time.


## To build

* Install dependencies: `python -m pip install jinja2 pandas`.
* Update data: edit `data/*.csv` files
* Render: `python render.py`. This produces HTML files at `docs/*.html`.
* Push changes to GitHub: `git add docs; git commit -m 're-rendered'; git push`. Make sure changes are in `main` branch.
* Check website: wait a minute then go to `https://halfasfast.com.au` to check the changes.


## Hosting and domain

GitHub Pages is used for hosting. HTML in the `docs/` folder in the `main` branch is automatically published to `https://liampingu.github.io`. Other GitHub Pages configuration is available under this repository's settings under "Pages".

The domain `halfasfast.com.au` is registered with GoDaddy, with "Forward with masking" option enabled. This embeds the Github Pages site with a HTML frame.
