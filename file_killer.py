import os
import shutil
import zipfile
import Resources.kill_apps_list
from color_text import print_suc, print_err, print_info, print_warn

empty_module_pack = os.path.join("Resources", "EmptyModulePack")  # 空模块模板位置
module_path = os.path.join("backup", "EmptyModulePack")  # 复制后模板位置
pack_state = False  # 保存寻找状态


# 精简apk
def delete_miui_apks(partitions_dict: dict, search_apk_dirs_list):
    global pack_state
    # 循环字典得到精简块
    for del_block_name, del_list in Resources.kill_apps_list.kill_app_dict.items():
        # 在精简之前，重置打包状态
        pack_state = False
        # 在精简之前，复制模板
        try:
            shutil.copytree(empty_module_pack, "backup/EmptyModulePack")
        except FileExistsError:
            # 若模板已经存在,则先清理模板
            clean_pack(module_path)
            shutil.copytree(empty_module_pack, "backup/EmptyModulePack")

        # 循环该精简块得到每一个apk
        for apk_name in del_list:
            location, partition_name, d = locate_apk(partitions_dict, apk_name, search_apk_dirs_list)
            # 三个参数只要其中一个不存在就马上换下一个
            if location is None:
                continue
            # 备份处理
            backup_apk(os.path.join(location, d), apk_name, partition_name, d)
            # 删除处理
            print_info(f"正在删除{apk_name}.apk.....")
            delete_apk(os.path.join(location, d, apk_name), apk_name)
        # 若该精简块所有apk均不存在,则不进行打包
        if pack_state:
            # 精简完毕,开始打包成apk
            compress_module(os.path.join("backup", f"{del_block_name}.zip"))
            print_suc(f"精简块: {del_block_name} 已成功生成.")
        else:
            # 不需要打包成模块
            print_info(f"精简块: {del_block_name} 不需要生成.")
        print("------------------------------------")


# 定位apk
def locate_apk(partitions_dict: dict, apk_name: str, apk_dirs_list: list):
    global pack_state
    # 循环位置轮番查找apk名文件夹
    for key, location in partitions_dict.items():
        # 空值直接下个位置
        if location is None:
            continue
        # 外循环依次查询最外层文件夹[app/priv-app]
        for d in apk_dirs_list:
            target_path = str(os.path.join(location, d))
            # 若该文件夹存在
            if os.path.exists(target_path):
                # 依次循环匹配
                for apks_dir in os.listdir(target_path):
                    # 若发现该文件夹下存在我们需要的特定名字的apk
                    if os.path.exists(os.path.join(location, d, apks_dir, f"{apk_name}.apk")):
                        # 同时返回目标位置、分区和外层文件夹,并且标记为有apk可打包
                        pack_state = True
                        return location, key, d

    # 若循环完毕依然无果
    print_warn(f"apk: {apk_name} 不存在!")
    return None, None, None


# 复制模板
def copy_module_pack():
    shutil.copy(empty_module_pack, "backup")


# 备份apk
def backup_apk(apk_path, apk_name, partition_name, dir_name):
    # 路径要存在
    if apk_path is None:
        return
    # 备份到模板中
    shutil.copytree(str(os.path.join(apk_path, apk_name)), str(os.path.join(
        "backup",
        "EmptyModulePack",
        partition_name,
        dir_name,
        apk_name
    )))


# 删除apk
def delete_apk(apk_path, apk_name):
    # 检查是否存在lib库
    if os.path.exists(os.path.join(apk_path, "lib")):
        # 若存在,则仅删除apk与oat
        try:
            os.remove(os.path.join(apk_path, f"{apk_name}.apk"))
            # 若也存在oat
            if os.path.exists(os.path.join(apk_path, "oat")):
                shutil.rmtree(os.path.join(apk_path, "oat"))
        except FileNotFoundError:
            print_err(f"在删除{apk_name}的lib时发生错误!")
    else:
        # 若不存在，则全部删除
        try:
            shutil.rmtree(apk_path)
        except FileNotFoundError:
            print_err(f"在删除apk{apk_name}时发生错误!")


# 模板打包成模块[通义千问写的]
def compress_module(output_path):
    # 创建一个ZipFile对象，并以写入模式打开
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # 遍历指定文件夹下的所有文件和子文件夹
        for root, dirs, files in os.walk(module_path):
            # 忽略最外层的文件夹名
            base_dir = os.path.basename(module_path)
            for file in files:
                # 构建完整的文件路径
                full_path = os.path.join(root, file)
                # 相对于文件夹的相对路径
                relative_path = os.path.relpath(full_path, module_path)
                # 写入到zip文件中，忽略与base_dir同级或以上的目录
                if not relative_path.startswith(base_dir):
                    # 这里是为了确保我们只添加文件夹内部的内容
                    zipf.write(full_path, arcname=relative_path)
    # 执行清理操作
    clean_pack(module_path)


# 清理模板
def clean_pack(module_folder_path):
    # 打包完毕,执行清理操作
    shutil.rmtree(module_folder_path)


# 清理模块打包环境
def clean_backup():
    # 删除
    shutil.rmtree("backup")
    # 创建新文件夹
    os.mkdir("backup")


# 清理 data-app
def data_app_cleaner(partitions_dict: dict):
    for partition_name, partition_location in partitions_dict.items():
        # 非None判断
        if partition_location is None:
            continue
        # 判断 data-app 目录是否存在
        data_apps_dir = os.path.join(partition_location, "data-app")
        if os.path.exists(data_apps_dir):
            # 删除并保留空文件夹
            shutil.rmtree(data_apps_dir)
            os.mkdir(data_apps_dir)
            print_suc(f"成功清空{partition_name}下的 data-app 文件夹.")


def clean_file_or_folder(file_or_folder_path):
    """
    清理无用文件
    :param file_or_folder_path: 文件或文件夹路径
    """
    # 判断文件类型
    if os.path.isdir(file_or_folder_path):
        try:
            shutil.rmtree(file_or_folder_path)
            print_suc(f"成功删除文件夹 {file_or_folder_path}.")
        except Exception as e:
            print_err(f"在删除文件夹时发生错误{e},请检查权限或文件夹是否被占用！")
    elif os.path.exists(file_or_folder_path):
        try:
            os.remove(file_or_folder_path)
            print_suc(f"成功删除文件 {file_or_folder_path}.")
        except Exception as e:
            print_err(f"在删除文件时发生错误{e},请检查权限或文件是否被占用！")
    else:
        print_err(f"无法找到文件/文件夹 {file_or_folder_path} , 可能已经被删除?")
