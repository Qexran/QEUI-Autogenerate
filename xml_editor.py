import os.path
import xml.etree.ElementTree as ET
from color_text import print_suc, print_err, print_info, print_warn
import re

# 描述修改状态
is_revised = False


def parse_xml_property(file_path: str, tag: str) -> dict:
    """
    对xml进行解析，并将结果保存成字典
    :param file_path: 文件路径
    :param tag: 要查找的标签
    """
    xml_dict = {}

    # 解析XML数据
    root = ET.parse(file_path).getroot()

    # 遍历XML元素并获取属性值
    for child in root:
        if child.tag == tag:
            # 去除默认格式 name: "x"
            name = child.attrib.get("name")

            # 若name为None则继续内处理
            if name is None:
                for sub_child in child:
                    sub_name = sub_child.attrib.get("name")

                    # 若name为None则跳过
                    if sub_name is None:
                        continue

                    sub_value = sub_child.text
                    xml_dict[sub_name] = sub_value
            else:
                # value无需处理
                value = str(child.text)
                xml_dict[name] = value

    return xml_dict


def edit_xml_property(file_path: str, mode: str, key: str = "", value: str = "") -> bool:
    """
    修改xml
    :param file_path: xml文件路径
    :param mode: 修改模式, add添加，rm删除，revise修改
    :param key: 键，必填
    :param value: 值，rm模式下可空，revise模式下为修改后的值
    """
    global is_revised

    # 首先文件要存在
    if not os.path.exists(file_path):
        print_err(f"无法找到xml文件: {file_path} !")
        return False

    # 新的临时文件
    tmp_path = file_path + ".tmp"

    def add():
        global is_revised
        # 读取XML文件
        with open(file_path, "r", encoding="utf-8") as f:
            # 找到最后一行，删除并添加新值
            lines = f.readlines()
            lines[len(lines) - 1] = f'    <bool name="{key}">{value}</bool>\n'
            lines.append("</features>")
            print_suc(f"成功添加值 【{key}:{value}】")
            is_revised = True
            # 写回文件
            with open(file_path, 'w', encoding='utf-8') as file:
                file.writelines(lines)
        if not is_revised:
            print_err(f"无法添加值 【{key}:{value}】.")

    def rm():
        global is_revised
        # 读取XML文件
        with open(file_path, "r", encoding="utf-8") as f, \
                open(tmp_path, "w", encoding="utf-8") as tmp_f:
            for line in f:
                if line.startswith(f'    <bool name="{key}"'):
                    print_suc(f"成功删除值 {key}")
                    is_revised = True
                    continue
                else:
                    tmp_f.write(line)
        # 覆盖源文件
        os.replace(tmp_path, file_path)
        if not is_revised:
            print_err(f"未找到值 {key} , 可能已经被移除或未被添加.")

    def revise():
        global is_revised
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            count = 0
            for i in lines:
                if i.startswith(f'    <bool name="{key}"'):
                    is_revised = True
                    lines[count] = f'    <bool name="{key}">{value}</bool>\n'
                    print_suc(f"成功将值 {key} 更改为 {value}.")
                count += 1

        # 写入文件
        with open(file_path, "w", encoding="utf-8") as f:
            f.writelines(lines)

        if not is_revised:
            print_err(f"没有找到值{key}.")

    if mode == "add":
        add()
    elif mode == "rm":
        rm()
    else:
        revise()

    return is_revised


if __name__ == '__main__':
    # result = parse_xml_property(os.path.join("Device_model", "lancelot.xml"), "gallery")
    # for x, y in result.items():
    #     print(f"键：{x}, 结果：{y}")
    edit_xml_property(os.path.join("Device_model", "exa.xml"), "rm", "is_qeui", "true")
