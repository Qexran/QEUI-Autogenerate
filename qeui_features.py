import os.path
import re
import shutil

import file_editor
import rom_getter
import xml_editor

from file_editor import edit_prop
from file_killer import clean_file_or_folder
from color_text import print_suc, print_err, print_info, print_warn

is_revised = False


def fuck_miui_lite(partitions_dict: dict):
    """
    去除miui低端限制[prop]
    ***未完成：安卓高版本其prop是否迁移到product
    """
    lite_properties = [
        "ro.config.low_ram.threshold_gb",
        "ro.config.low_ram.version"
    ]

    for p in lite_properties:
        edit_prop(
            os.path.join(partitions_dict["system"], "build.prop"),
            "rm",
            p
        )


def delete_service(partitions_dict: dict):
    """
    删除无用服务
    """
    useless_services = [
        "mdnsd",
    ]

    for s in useless_services:
        clean_file_or_folder(os.path.join(partitions_dict["system"], "bin", s))
        clean_file_or_folder(os.path.join(partitions_dict["system"], "etc", "init", f"{s}.rc"))


def develop_mode(partitions_dict: dict, state: bool):
    """
    debug模式，用于ROM的适配工作
    state: 开启状态
    """
    if not state:
        return

    prop_list = rom_getter.get_default_prop(partitions_dict)

    for p in prop_list:
        # 将persist.sys.usb.config属性从none改为adb
        edit_prop(
            p,
            "revise",
            "persist.sys.usb.config",
            "none",
            "adb"
        )
        # 将ro.debuggable属性设置为1，允许通过ADB进行调试
        edit_prop(
            p,
            "revise",
            "ro.debuggable",
            "0",
            "1"
        )
        # 将ro.adb.secure属性设置为0，可能允许更宽松的ADB权限，或禁用某些安全措施
        edit_prop(
            p,
            "revise",
            "ro.adb.secure",
            "1",
            "0"
        )
        edit_prop(
            p,
            "add",
            "ro.force.debuggable",
            "1",
        )


def add_data_apps(partitions_dict: dict) -> bool:
    """
    为ROM添加自定义的data-app
    :param partitions_dict: 分区位置表
    """
    # 导入到
    target_dir = os.path.join(partitions_dict["system"], "data-app")

    if os.path.exists(target_dir):
        shutil.rmtree(target_dir)
    try:
        shutil.copytree(os.path.join("Resources", "data-app"), target_dir)
    except FileExistsError as e:
        print_err(f"在复制 data-app 时发生异常：{e}")
        return False

    return True


def add_features(feature_files_list: list, miui_version: str) -> bool:
    """
    xml层面上添加设备不支持的功能
    :param feature_files_list: 需要处理的xml
    :param miui_version: MIUI版本
    """

    # 默认的存放mod_xml位置
    mod_xml_path = os.path.join("Resources", "new_feature.xml")

    # 外层循环分别对多个文件进行处理
    for f in feature_files_list:
        # 内层循环遍历得到的xml字典
        mod_features = xml_editor.parse_xml_property(mod_xml_path, "MIUI" + miui_version)

        print(mod_features)

        for k, v in mod_features.items():
            xml_editor.edit_xml_property(
                f,
                "add",
                k,
                v
            )

    return True


def add_build_properties(partitions_dict: dict, revise_p_name: str = "system") -> bool:
    """
    为ROM添加新的prop信息
    :param revise_p_name: 需要更改prop的分区，默认为system
    :param partitions_dict: 分区地址表
    """
    # 默认的mod_prop文件位置
    mod_prop_path = os.path.join("Resources", "new_build_prop.txt")

    # 需要修改的文件位置
    target_prop_path = os.path.join(partitions_dict[revise_p_name], "build.prop")

    # 临时文件位置
    tmp_path = os.path.join(partitions_dict[revise_p_name], "build.prop.tmp")

    if not os.path.exists(target_prop_path):
        return False

    with open(mod_prop_path, "r", encoding="UTF-8") as f, \
            open(target_prop_path, "r", encoding="UTF-8") as o:
        mod_lines = f.readlines()
        org_lines = o.readlines()

        with open(tmp_path, "w", encoding="UTF-8") as ff:
            for line in org_lines:
                ff.write(line)
            for line in mod_lines:
                ff.write(line)

    # 最后再替换文件
    os.replace(tmp_path, target_prop_path)

    return True


def close_gps_log(partitions_dict: dict) -> bool:
    """
    关闭GPS日志
    :param partitions_dict: 分区地址表
    """

    global is_revised

    # log文件路径
    log_path = os.path.join(partitions_dict["system"], "etc", "gps_debug.conf")

    # 临时文件位置
    tmp_log_path = os.path.join(partitions_dict["system"], "etc", "gps_debug.conf.tmp")

    if not os.path.exists(log_path):
        return is_revised

    # 正则表达式
    regex = re.compile("NMEA_LEN=\\d+")

    with open(log_path, "r", encoding="UTF-8") as log, \
            open(tmp_log_path, "w", encoding="UTF-8") as tmp:
        for line in log:
            if regex.match(line):
                is_revised = True
                tmp.write("NMEA_LEN=0")
            else:
                tmp.write(line)

    os.replace(tmp_log_path, log_path)

    return is_revised


def replace_media_files(partitions_dict: dict) -> bool:
    # 定义位置
    media_path = os.path.join(partitions_dict["system"], "media")
    wallpaper_path = os.path.join(media_path, "wallpaper")
    theme_path = os.path.join(media_path, "theme")
    theme_default_path = os.path.join(theme_path, "default")
    icons_path = os.path.join(theme_path, "miui_mod_icons")
    # boot_anim_path = os.path.join(media_path, "bootanimation.zip")

    # 开机无声
    file_editor.copy_file_from_resource("bootaudio.mp3", media_path)

    # 替换动态图标
    try:
        shutil.rmtree(icons_path)
    except Exception as e:
        print_err(f"删除目录 {icons_path} 时发生错误：{e}")

    file_editor.copy_file_from_resource("icons", theme_default_path)

    # 删除壁纸(组)
    try:
        shutil.rmtree(wallpaper_path)
    except Exception as e:
        print_err(f"删除目录 {wallpaper_path} 时发生错误：{e}")

    old_wallpaper_path1 = os.path.join(media_path, "lockscreen")  # 旧ROM锁屏壁纸路径
    old_wallpaper_path2 = os.path.join(media_path, "wallpaper")  # 旧ROM桌面壁纸路径

    if os.path.exists(old_wallpaper_path1):
        os.remove(old_wallpaper_path1)

    if os.path.exists(old_wallpaper_path2):
        os.remove(old_wallpaper_path2)

    # 去除自动安装
    etc_path = os.path.join(partitions_dict["system"], "etc")

    file_editor.mk_none_file("auto-install.json", etc_path)
    file_editor.mk_none_file("auto-install2.json", etc_path)

    # 无级调节相关
    file_editor.copy_file_from_resource("com.miui.home", theme_default_path)

    # 高级电源菜单布局
    file_editor.copy_file_from_resource("powermenu", theme_default_path)

    # 替换开机动画
    file_editor.copy_file_from_resource(
        "new-bootanimation.zip",
        media_path,
        "bootanimation.zip")

    # 合成作者信息
    # 待施工......

    return True


def unlock_removable_apks_from_miuihome(partitions_dict: dict) -> bool:
    """
    解锁可移除桌面应用限制
    :return:
    """
    file_editor.copy_file_from_resource(
        "removable_apk_info.xml",
        os.path.join(partitions_dict["product"], "etc")
    )


def pangu_back_system(partitions_dict: dict) -> bool:
    """
    正在搬运pangu内部分文件
    :param partitions_dict:
    :return:
    """
    pangu_path = os.path.join(partitions_dict["product"], "pangu", "system")

    move_dict = [
        # From : To
        os.path.join("app", "Joyose"),
        os.path.join("app", "NQNfcNci"),
        "etc",
        "framework",
    ]

    # 首先pangu文件夹要存在
    if not os.path.exists(pangu_path):
        print_info("此ROM不支持pangu架构,不进行搬运.")
        return False

    # 外层循环搬运列表内容
    for v in move_dict:
        src_path = os.path.join(pangu_path, v)

        # 首先目标文件夹要存在
        if not os.path.exists(src_path):
            print_info(f"文件 {src_path} 不存在, 不进行移动/合并")
            continue

        # 再进行移动操作
        dest_path = os.path.join(partitions_dict["system"], v)
        file_editor.move_exist_folder(src_path, dest_path)
        print_suc(f"成功将 {src_path} 从 pangu 转移到 system .")

    return True


# $$$$$$$$$$$$$$$$$$$$$$$$$$
"""
function magiskBootPatch(){
    #载入配置
    function changeCoreConfigs(){
        #删除
        rm -rf Magisk_BootPatch/magisk32
        rm -rf Magisk_BootPatch/magisk64
        rm -rf Magisk_BootPatch/magiskinit
        #复制
        cp -r Magisk_BootPatch/$1/magisk32 Magisk_BootPatch
        cp -r Magisk_BootPatch/$1/magisk64 Magisk_BootPatch
        cp -r Magisk_BootPatch/$1/magiskinit Magisk_BootPatch
    }

    #用法 magiskBootPatch [版本:23.0/Magisk/Delta] 镜像路径[若有]
    #[Tag:REPLACE 直接替换原来的boot.img]
    if [[ $1 ]]; then
        changeCoreConfigs $1
    else
        echo "- FAILED TO LOAD CONFIGS!"
        exit
    fi

    BOOTIMG_PATH=$2
    source Magisk_BootPatch/boot_patch.sh 
}
"""


def magisk_bootpatch(magisk_version: str, style: str) -> bool:
    """
    对boot镜像进行修补
    :param magisk_version: magisk版本,可选【】
    :param style: Magisk类型【Magisk/Delta】
    :return: 修补成功与否
    """
    



if __name__ == "__main__":
    p_dict = rom_getter.get_rom_structure("workspace", "system")

    # print_info("删去低端标识字段")
    # fuck_miui_lite(p_dict)
    #
    # print_info("删除无用服务")
    # delete_service(p_dict)
    #
    # print_info("开启开发者模式")
    # develop_mode(p_dict, True)
    #
    # print_info("添加data-app")
    # add_data_apps(p_dict)
    #
    # print_info("xml层面上添加设备不支持的功能")
    # add_features(
    #     rom_getter.get_device_feature(p_dict),
    #     rom_getter.catch_device_information(rom_getter.get_prop_files(p_dict))["MIUI_VERSION"]
    # )
    #
    # print_info("prop增强")
    # add_build_properties(p_dict)
    #
    # print_info("关闭GPS日志")
    # close_gps_log(p_dict)

    # print_info("基础修改:")
    # print_info("移除开机音乐[可恢复]")
    # print_info("完美图标计划")
    # print_info("删除壁纸(组)")
    # print_info("去除自动安装")
    # print_info("桌面布局无级调节")
    # print_info("高级电源菜单")
    # replace_media_files(p_dict)

    # print_info("解锁可移除桌面应用限制")
    # unlock_removable_apks_from_miuihome(p_dict)

    # print_info("搬运pangu内部分文件")
    pangu_back_system(p_dict)
