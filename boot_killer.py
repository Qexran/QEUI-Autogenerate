import fnmatch
import os.path
import shutil
from pack import run_win_program

AIK = "bin/win32_program/AIK"


# 清理环境
def clean_dir(dir_name: str):
    if os.path.exists(f"{AIK}/{dir_name}"):
        shutil.rmtree(f"{AIK}/{dir_name}")


def clean_file(file: str):
    if os.path.exists(file):
        os.remove(file)


# 解包boot
def un_boot(work_path, image_name):
    # 清道夫
    clean_dir("ramdisk")
    clean_dir("split_img")
    clean_file(f"{AIK}/{image_name}.img")
    clean_file(f"{AIK}/qe_{image_name}.img")

    # 将镜像移动到 AIK 中
    shutil.move(f"{work_path}/{image_name}.img", AIK)

    # 运行解包程序
    run_win_program("unpackimg.bat", "")

    # 检查是否解包成功
    if not os.path.exists(f"{AIK}/split_img"):
        print(f"- 解包 {image_name}.img 失败!")
        exit()

    # 返回ramdisk和split_img路径
    return f"{AIK}/ramdisk", f"{AIK}/split_img"

# 解锁 vbmeta.img
def unlock_vbmeta(work_path, need_unlock_vbmeta_list):
    for vbmeta_file in need_unlock_vbmeta_list:
        if os.path.exists(vbmeta_file):
            # 写入的位置（从0开始计数）
            offset = 123
            # 要写入的字节（注意Python中的字节字符串需要前缀b）
            data_to_write = b'\x02'

            # 以二进制读写模式打开文件
            with open(vbmeta_file, 'r+b') as file:
                # 移动文件指针到指定位置
                file.seek(offset)
                # 写入数据
                file.write(data_to_write)

            print(f"- Byte 02 has been written to position {offset} in {vbmeta_file}")


# 打包boot
def re_boot(work_path, image_name):
    # 打包boot.img
    run_win_program("repackimg.bat", "")

    # 清道夫
    clean_dir("ramdisk")
    clean_dir("split_img")
    clean_file(f"{AIK}/{image_name}.img")

    # 检查是否打包完毕
    if not os.path.exists(f"{AIK}/qe_{image_name}.img"):
        print(f"- 打包 {image_name}.img 失败!")


# 去除data强制加密【未完工】
def fuck_data_cryption(process_path) -> bool:
    fstab_files = []
    # 查找所有相关文件
    for path, dirs, files in os.walk(f"{AIK}/{process_path}"):
        for file in files:
            if fnmatch.fnmatch(file, "fstab.*"):
                fstab_files.append(file)

    #开始处理
    for fstab_file in fstab_files:
        pass



