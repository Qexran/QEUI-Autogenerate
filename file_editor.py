import os.path
import shutil
from color_text import print_suc, print_err, print_warn, print_info


def move_exist_folder(src_path, dest_path):
    """
    移动已经存在的文件夹
    """
    # 目标文件(夹)不存在，则直接移动文件夹
    if not os.path.exists(dest_path):
        shutil.move(src_path, dest_path)
    else:
        # 存在，则循环改文件夹依次搬运其中的文件
        for f in os.listdir(src_path):
            f_path = os.path.join(src_path, f)
            d_path = os.path.join(dest_path, f)
            # 若是文件夹，则递归搬运
            if os.path.isdir(f_path):
                move_exist_folder(f_path, d_path)
            else:
                # 文件直接覆盖
                shutil.move(f_path, d_path)
        # 最后删除空文件夹
        os.rmdir(src_path)


def copy_file_from_resource(file_name: str, destination: str, new_name: str = ""):
    """
    该方法用于从资源中复制文件到ROM(覆盖)
    :param file_name: 在Resource中的文件路径
    :param destination: 目标路径(不需要再次填写文件名)
    """
    # 合成完整路径
    tools_dir = os.path.join("Resources", "Copy", file_name)

    if new_name == "":
        destination = os.path.join(destination, file_name)
    else:
        destination = os.path.join(destination, new_name)

    if os.path.isdir(tools_dir):
        try:
            if os.path.exists(destination):
                # 文件夹原来存在,先清空目标文件夹的内容
                shutil.rmtree(destination)
            # 再复制过去
            shutil.copytree(tools_dir, destination)
            print_suc(f"成功将文件夹 {file_name} 复制到 {destination}.")
        except FileNotFoundError as e:
            print(f"- 文件夹 {file_name} 不存在！请检查工具是否完整！")
    else:
        try:
            # 再复制过去
            shutil.copy(tools_dir, destination)
            print_suc(f"成功将文件 {file_name} 复制到 {destination}.")
        except FileNotFoundError as e:
            print(f"- 文件 {file_name} 不存在！请检查工具是否完整！")


def edit_prop(prop_path: str, edit_mode: str, property_name="", property_value="", revise_value=""):
    """
    该方法用于编辑prop文件
    :param prop_path:prop路径
    :param edit_mode:编辑模式，可选三个，一个rm,一个revise,一个add
    :param property_name:属性名
    :param property_value:属性值【可空】
    :param revise_value:修改之后的值,只有在revise模式下生效【可空】
    """

    # 若文件本身不存在，则直接报错
    if not os.path.exists(prop_path):
        print_err(f"无法找到 {prop_path} 文件！")
        return

    prop_temp = prop_path + ".tmp"

    # 增加属性
    def add_property():
        with open(prop_path, "a", encoding="utf-8") as f:
            if property_name != "" and property_value != "":
                f.write(property_name + "=" + property_value + "\n")
                print_suc(f"成功向 {prop_path} 文件添加了属性值 {property_name + "=" + property_value}")
            else:
                print_err(f"从函数中获取属性 {property_name} 失败！")

    def rm_property():
        is_edited = False
        # 以读模式获取文本
        # 以写模式写入temp
        with open(prop_path, "r", encoding="utf-8") as f, \
                open(prop_temp, "w", encoding="utf-8") as tmp_f:
            for line in f:
                # 遇到匹配行
                if line.startswith(property_name + "=" + property_value):
                    is_edited = True
                    # 若要修改值
                    if revise_value != "":
                        # 则修改为新值
                        tmp_value = property_name + "=" + revise_value + "\n"
                        tmp_f.write(tmp_value)
                        print_suc(
                            f"成功将 {prop_path} 文件中的属性值 {property_name} 从 {property_value} 更改为 {revise_value}")
                    else:
                        print_suc(f"成功删除 {prop_path} 文件中的属性值 {property_name}")
                        # 否则直接跳过
                        continue
                elif line != "\n":
                    # 其他行保持正常,排除掉空行
                    tmp_f.write(line)

            if not is_edited:
                if revise_value != "":
                    print_err(f"无法找到 {prop_path} 文件中的属性值 {property_name} , 跳过修改！")
                else:
                    print_err(f"无法找到 {prop_path} 文件中的属性值 {property_name} , 跳过删除！")

        # 替换掉原prop文件
        os.replace(prop_temp, prop_path)

    if edit_mode == "add":
        add_property()
    else:
        rm_property()


def mk_none_file(file_name: str, to_path: str):
    tmp_file = os.path.join(to_path, file_name + ".tmp")
    with open(tmp_file, "w", encoding="UTF-8") as f:
        f.write("")
    os.replace(tmp_file, os.path.join(to_path, file_name))


if __name__ == "__main__":
    edit_prop("C:/MySoftware/ROM/QEUI-GenerateTool/workspace/system/system/system/build.prop",
              "rm",
              "qe.tool"
              )
