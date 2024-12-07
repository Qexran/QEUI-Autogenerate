import os
import re
from color_text import print_suc, print_err, print_warn, print_info

# QEUI需要处理的额外分区[system在函数内加不计入查找范围内]
qeui_partitions = ["vendor", "product", "system_ext", "mi_ext"]


# 获取build.prop信息
def get_prop(work_path, rom_structure):
    # 寻找所有prop
    prop_probably_path = ["system", "vendor", "product"]


"""
    简述以下代码原理
    循环外分区字典,得到嵌套信息
      检查路径是否合法
      是
          该路径作为最终路径
      否
          循环内嵌分区字典，得到内置分区信息
              检查路径是否合法
                  是
                      该路径作为最终路径
                  否
                      该分区路径不存在/进入GSI特殊检查
"""


# 获取prop基本信息
def get_prop_files(partitions_dict: dict) -> list:
    prop_files_list = []  # rom内的所有prop文件

    # 抓取目标目录内所有prop文件
    def catch_prop_file(partition_name):
        directory = partitions_dict.get(partition_name)
        # 若没有目录, 则不抓取
        if directory is None:
            return
        # 遍历目录内容做出后辍名判断
        for file in os.listdir(directory):
            path = os.path.join(directory, file)
            if path.endswith(".prop"):
                # 去掉不必要的prop
                if not path.endswith((
                        "ro.prop",
                        "rw.prop",
                        "build_dsds_vendor.prop",
                        "build_ss.prop",
                        "build_dsds.prop",
                        "build_ss_vendor.prop",
                        "default.prop"  # 有专门的方法处理default.prop,这里不引入列表
                )):
                    # 加进列表
                    prop_files_list.append(path)

    # 优先找system分区
    catch_prop_file("system")
    # 再找额外分区的
    for i in qeui_partitions:
        catch_prop_file(i)

    # 使用 sorted() 函数按路径的最后一部分长度升序排序
    sorted_paths = sorted(prop_files_list, key=lambda path: len(os.path.basename(path)))
    return sorted_paths


def get_default_prop(partitions_dict: dict) -> list:
    """
    获取default.prop
    返回prop文件列表
    """
    default_prop_list = []

    def catch_default_prop(partition_name):
        # system 的default文件在etc内
        if partition_name == "system":
            out_path = os.path.join(partitions_dict[partition_name], "etc")
        else:
            # 在其他分区的情况
            out_path = partitions_dict[partition_name]

        # 若无etc文件夹则直接报错
        if not os.path.exists(out_path):
            print_err(f"文件夹 {out_path} 不存在！")
            return

        for i in os.listdir(out_path):
            path = os.path.join(out_path, i)
            if i.endswith(("prop.default", "default.prop")):
                default_prop_list.append(path)

    # 一般文件在system分区中
    catch_default_prop("system")
    # vendor中也有
    # catch_default_prop("vendor")

    return default_prop_list


def get_device_feature(partitions_dict: dict) -> list:
    """
    获取device_feature文件
    """
    device_feature_list = []

    def check_file_and_add(p_name):
        # 分区非空判断
        if partitions_dict[p_name] is None:
            return

        system_feature_dir = os.path.join(partitions_dict[p_name], "etc", "device_features")
        try:
            # 正则判断xml文件
            regex = re.compile(".*.xml")
            for f in os.listdir(system_feature_dir):
                if regex.match(f):
                    print_info(f"在 {p_name} 中发现设备特性文件 {f}")
                    device_feature_list.append(os.path.join(system_feature_dir, f))
        except FileNotFoundError:
            print_warn(f"在 {p_name} 中没有发现 device_feature！")

    # 先找system
    check_file_and_add("system")
    # 再找product
    check_file_and_add("product")
    # 最后vendor
    check_file_and_add("vendor")

    return device_feature_list


def catch_device_information(prop_files_list: list) -> dict:
    """
    抓取prop信息
    :param prop_files_list: prop文件表
    :return: 返回prop信息字典
    """

    # 传入prop文件与属性,返回值
    def get_prop_value(file: str, prop: str):
        try:
            with open(file, "r", encoding="UTF-8") as f:
                # 循环得到每一行
                for line in f:
                    if prop in line:
                        value = line.split("=")[1].strip()
                        if value != "":
                            return value
                        else:
                            return None
        except FileNotFoundError:
            print(f"- 获取失败!文件不存在")

    # QEUI需要获取的属性
    property_dict = {
        "ANDROID_VERSION": None,  # 安卓版本
        "SDK_VERSION": None,  # SDK版本
        "DEVICE": None,  # 设备代号
        "PRODUCT_NAME": None,  # 设备名称
        "LANGUAGE": None,  # 默认语言
        "MIUI_VERSION": None,  # MIUI版本
    }

    # 方案,也就是prop文件中获取这些值所需要的属性
    plan_dict = {
        "ANDROID_VERSION": [  # 安卓版本
            "ro.system.build.version.release",
            "ro.build.version.release"
        ],
        "SDK_VERSION": [  # SDK版本
            "ro.system.build.version.sdk",
            "ro.build.version.sdk"
        ],
        "DEVICE": [  # 设备代号
            "ro.product.vendor.device",
            "ro.build.product"
        ],
        "PRODUCT_NAME": [  # 设备名称
            "ro.product.system.marketname",
            "ro.product.system.model",
            "ro.product.marketname",
            "ro.product.vendor.marketname",
        ],
        "LANGUAGE": [  # 默认语言
            "ro.product.locale"
        ],
        "MIUI_VERSION": [  # MIUI版本
            "ro.build.version.incremental"
        ],
    }

    # 特殊规则,防止获取到mssi一类的数值
    def check_value(pt_name, value):
        # 对于MIUI版本，一般只需要获取V到第一个.[12.5是第二个]之间的数值
        if pt_name == "MIUI_VERSION":
            # 正则表达式过滤
            regex_dict = {
                "11": re.compile("V11"),
                "12": re.compile("V12\\.0"),
                "12.5": re.compile("V12\\.5"),
                "13": re.compile("V13"),
                "14": re.compile("V14")
            }
            for k, v in regex_dict.items():
                if v.match(value):
                    return k

        return value

    # 第一层循环得到属性对应的获取方案
    for property_name, plans in plan_dict.items():
        # 第二层循环多方案获取，以保证成功获取到值
        for plan in plans:
            # 第三层prop文件查找信息,优先build.prop,再找其他prop
            for prop_file in prop_files_list:
                # 抓取信息,获取值并进行校验
                result = check_value(property_name, get_prop_value(prop_file, plan))
                # 若结果非空,则存入字典
                if result is not None:
                    property_dict[property_name] = result
                    # 结束查找其他prop文件
                    break
            # 若已有结果，则结束其他方案
            if property_dict[property_name] is not None:
                break

    return property_dict


def get_rom_structure(work_path, scan_to_inner_partition) -> dict:
    """
    获取ROM各分区路径[已经包含工作环境路径,一键直达]
    :param work_path: 工作环境,默认为 workspace
    :param scan_to_inner_partition: 如果存在分区套分区的情况,则需要深入查找的分区名,一般是system
    """

    # 检查路径是否合法[即分区内有内容]
    def check_partition_is_legal(too_long_path: str):
        if os.path.isdir(os.path.join(str(too_long_path), "etc")):
            # 校验合法, 直接返回路径
            return too_long_path
        else:
            return None

    # 若找不到独立分区,则判断是否存在内部的 product 等分区
    def get_inner_partition_path(partition, scan_partition):
        # 这里的意思是存在内部分区目录内的任意有效文件,这里以 etc 目录作为例子
        # 由于大概率是要在 scan_partition 内部寻找分区,故需要再进一层 scan_partition
        too_long_path = os.path.join(work_path, scan_partition, scan_partition, scan_partition, partition)
        check_partition_is_legal(str(too_long_path))

    # 判断是否有独立打包的分区
    def get_single_partition_path(partition, scan_partition):
        # 这里的意思是存在外部分区目录内的任意有效文件,这里以 etc 目录作为例子
        # 由于是检查外部分区,故不需要考虑system再嵌套一层的情况
        too_long_path = os.path.join(work_path, partition, partition)
        result = check_partition_is_legal(str(too_long_path))
        if result is None:
            return get_inner_partition_path(partition, scan_partition)
        else:
            return result

    # 遍历写入字典
    partitions_information = {}
    for p in qeui_partitions:
        partitions_information.update({p: get_single_partition_path(p, scan_to_inner_partition)})
    # system分区单独处理
    partitions_information.update({"system": os.path.join(work_path, "system", "system", "system")})

    return partitions_information


if __name__ == '__main__':
    s = get_rom_structure("workspace", "system")
    # print(s)
    # files = get_prop_files(s)
    # print(files)
    # d_files = get_default_prop(s)
    # print(d_files)
    # print("==============================")
    # print(catch_device_information(files))
    fl = get_device_feature(s)
