from jinja2 import Template, Markup
import glob

from config import URL

files = glob.glob("*.html")
# python_files = glob.glob("*.py")
# files.extend(python_files)

pages = []
imports = []
for each_file in files:
    with open(each_file) as f:
        if "<!DOCTYPE html>" in next(f).rstrip():
            pages.append(each_file)
        # elif not ".py" in each_file:
        else:
            imports.append(each_file)

imports.append("checkout.js")
imports.append("schedule.py")
imports.append("cart.py")
imports.append("sessions.py")
imports.append("profile.py")
imports.append("create.py")
imports.append("config.py")

args = {}
for each_import in imports:
    name = each_import.split(".")[0]
    with open(each_import) as f:
        import_html = f.read().replace("{URL}", URL)
    args[name] = import_html

# with open("footer.html") as f:
    # footer = f.read()
# args["footer"] = footer
print(imports, pages)

for each_file in pages:
    with open(each_file) as f:
        html = f.read().rstrip()
        template = Template(html)
        rendered = template.render(**args).replace("{URL}", URL)

    with open("precompile/" + each_file, "w") as f:
        f.write(rendered)

for each_file in imports:
    with open(each_file) as f:
        html = f.read().rstrip().replace("{URL}", URL)

    with open("precompile/" + each_file, "w") as f:
        f.write(html)
