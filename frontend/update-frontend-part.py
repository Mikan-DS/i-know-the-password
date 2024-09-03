import glob
import os
import shutil

if os.path.basename(os.getcwd()) != 'i-know-the-password-frontend':
    os.chdir('i-know-the-password-frontend')
os.system('npm run build')

with open("../template.html", "r", encoding="UTF-8") as file:
    template = file.read()

# Получаем список файлов в директории
js_files = glob.glob('build/static/js/*.js')

shutil.rmtree("../static/frontend/js/", ignore_errors=True)
os.makedirs("../static/frontend/js/", exist_ok=True)
# Копируем файлы в нужную директорию
js_file = [i for i in js_files if "main" in os.path.basename(i)][0]
shutil.copy(js_file, f'../static/frontend/js/{os.path.basename(js_file)}')

# Получаем список файлов в директории
css_files = glob.glob('build/static/css/*.css')

shutil.rmtree("../static/frontend/css/", ignore_errors=True)
os.makedirs("../static/frontend/css/", exist_ok=True)
# Копируем файлы в нужную директорию
css_file = [i for i in css_files if "main" in os.path.basename(i)][0]
shutil.copy(css_file, f'../static/frontend/css/{os.path.basename(css_file)}')

if os.path.exists("build/static/media"):
    shutil.rmtree("../static/media", ignore_errors=True)
    shutil.copytree("build/static/media", "../static/media", dirs_exist_ok=True)

with open("../templates/frontend/app.html", "w", encoding="UTF-8") as file:
    file.write(template % (os.path.basename(js_file), os.path.basename(css_file)))

os.chdir('../static')
os.system('git add ./frontend/')
if os.path.exists("./media"):
    os.system('git add ./media/')
