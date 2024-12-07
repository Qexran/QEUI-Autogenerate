import fnmatch
import os
import re
import shutil
import zipfile
from color_text import print_suc, print_err, print_info, print_warn

# 运行win32程序
from pack import run_win_program


# 解压压缩文件
def unzip_file(zip_filepath, path):
    # 打开ZIP文件
    with zipfile.ZipFile(zip_filepath, 'r') as zip_ref:
        print_info("正在解压...")
        # 解压所有文件到目标目录
        zip_ref.extractall(path)
        print_suc(f"解压 {zip_filepath} 完成!")


# 解包镜像文件
def unpack_image(work_path, rom_style, need_unpack_list):
    def un_br(target):
        run_win_program("brotli.exe", f"-j -d {work_path}/{target}.new.dat.br")
        # 该程序自带删除源文件功能，无需再写删除代码
        un_dat(target)

    def un_dat(target):
        mixed = f"{work_path}/{target}"
        try:
            os.system(
                f"python bin/sdat2img.py %s.transfer.list %s.new.dat %s.img" % (mixed, mixed, mixed))
        except:
            print_err(f"解包 {target}.new.dat 失败! 请检查rom包是否正常!")
        else:
            os.remove("%s.new.dat" % mixed)
            un_img(target)

    def un_img(target):
        mixed = f"{work_path}/{target}"
        try:
            os.system(f"python3 bin/imagextractor.py %s.img %s" % (mixed, work_path))
        except:
            os.remove("%s.img" % mixed)
            print_err(f"解包 {target}.img 失败! 请检查rom包是否正常!")
            exit()

        # img解包完毕后需要让分区独立起来
        os.mkdir(f"{work_path}/{target}1")
        shutil.move(f"{work_path}/{target}", f"{work_path}/{target}1")
        shutil.move(f"{work_path}/config", f"{work_path}/{target}1")
        os.rename(f"{work_path}/{target}1", f"{work_path}/{target}")

    if rom_style == "br":
        # 解br
        for i in need_unpack_list:
            un_br(i)
    elif rom_style == "dat":
        for i in need_unpack_list:
            un_dat(i)
    elif rom_style == "img":
        for i in need_unpack_list:
            un_img(i)
    print_suc(f"rom解包完毕,开始进行修改.")


# 查找文件
def find_files(directory, content) -> str:
    for root, dirs, files in os.walk(directory):
        for basename in files:
            if fnmatch.fnmatch(basename, content):
                filename = os.path.join(root, basename)
                yield filename


# 确定rom类型并解包
def check_rom_and_unpack(path, operate_list) -> list:
    # 根据查找结果返回列表
    def list_for_result(paths, content) -> list:
        return list(find_files(paths, content))

    # 判断列表内是否有内容
    if list_for_result(path, "*.dat.br"):
        rom_style = "br"
    elif list_for_result(path, "*.new.dat"):
        rom_style = "dat"
    elif list_for_result(path, "*.img"):
        rom_style = "img"
    else:
        print_err(f"rom类型识别失败!请确定rom打包方式是否正规或rom有无损坏!")
        exit()

    need_unpack_list: list = []
    for i in list_for_result(path, f"*.{rom_style}"):
        # 去除前缀
        i = i.replace(f'{path}\\', '')
        # 正则表达式比较
        for j in operate_list:
            regex = re.compile(f"{j}.*")
            if regex.match(i):
                need_unpack_list.append(j)

    print_info(f"当前打包方式为:{rom_style},即将开始解包.")
    print_info(f"需要解包的条目如下:{need_unpack_list}")

    unpack_image(path, rom_style, need_unpack_list)

    return need_unpack_list
