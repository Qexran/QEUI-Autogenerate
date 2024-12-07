import fnmatch
import os.path
import shutil
import subprocess
import re
from color_text import print_suc, print_err, print_info, print_warn

smali = os.path.join("bin", "jar_tools", "smali.jar")
baksmali = os.path.join("bin", "jar_tools", "baksmali.jar")
apktool = os.path.join("bin", "jar_tools", "apktool.jar")

style_name = {
    "code": "代码",
    "string": "字符串",
    "class": "类名",
    "method": "方法名"
}


def get_line_num_belongs_method(
        lines: list,
        line_num: int,
):
    """
    获取行号在文件所在位置所属的方法名的行号
    :param lines: 文件内容
    :param line_num: 行号【当前】
    :return: 方法所在行号【下标索引】
    """

    while not lines[line_num].startswith(".method"):
        # 防止越界
        if line_num == 0:
            print_err("错误：无法获取行号在文件所在位置所属的方法名的行号")
            return 0
        line_num -= 1

    print_info(f"成功获取行号在文件所在位置所属的方法名的行号 {line_num + 1}")
    return line_num


def get_method_range_lines(
        lines: list,
        method_name: str,
        method_line_num: int = None,
        is_complete_match: bool = False
) -> list:
    """
    用于定位某个方法所占的行号区间【索引】
    :param lines: readlines读取到的文件内容
    :param method_name: 要查找的方法名
    :param method_line_num: 方法名行号[若有]
    :param is_complete_match: 全词匹配[默认否]
    :return: .register到.end method在内的行号区间
    """

    def get_num(n: int) -> list:

        # list下一位即是开始区间
        n += 1
        num_range_list = [n]

        while not lines[n].startswith(".method"):
            # 防止越界
            if len(lines) == n:
                break
            n += 1

        # 结束区间即循环去掉空行之后的结果
        num_range_list.append(n - 1)

        print_info(f"成功获取方法区间[ {num_range_list[0]} , {num_range_list[1]} ]")
        return num_range_list

    # 如果已经有结果行号，无需再次定位方法名
    if method_line_num is not None:
        return get_num(method_line_num)

    # 获取方法名
    regex = re.compile(method_regex(is_complete_match, method_name))
    i = 0
    for ll in lines:
        if regex.match(ll):
            return get_num(i)
        i += 1


def method_regex(complete_match_status: bool, method_name: str) -> str:
    """
    定义方法名的正则表达式
    :param complete_match_status: 是否启用全词匹配
    :param method_name: 方法名
    :return: 匹配该方法名的正则表达式
    """
    if complete_match_status:
        return (f"\\.method\\s(public|protected|private)?\\s?"
                f"(abstract|static)?\\s?(constructor)?\\s?(final)?\\s?"
                f"<?{method_name}>?\\(.*\\)(Z|V|I|.*;)")
    else:
        return (f"\\.method\\s(public|protected|private)?\\s?"
                f"(abstract|static|constructor)?\\s?(constructor)?\\s?(final)?\\s?"
                f"<?\\w*{method_name}\\w*>?\\(.*\\)(Z|V|I|.*;)")


def get_register_type(register_line: str):
    """
    获取行首的类型
    :param register_line: 行首
    :return: 返回类型
    """
    type_dict = {
        "locals": re.compile("\\.locals"),
        "registers": re.compile("\\.registers"),
    }
    for k, v in type_dict.items():
        if v.match(register_line):
            print_info(f"成功获取到寄存器类型: {v}")
            return k

    print_err("错误: 无法找到行首对应的类型！")
    return None


def get_method_type(method_name: str):
    """
    获取方法对应返回值类型
    :param method_name: 传入的方法名的那一行
    :return: 返回类型
    """

    type_dict = {
        "Z": re.compile("\\.method.*Z$"),
        "I": re.compile("\\.method.*I$"),
        "J": re.compile("\\.method.*J$"),
        "V": re.compile("\\.method.*V$"),
        ";": re.compile("\\.method.*;$"),
    }

    for k, v in type_dict.items():
        if v.match(method_name):
            print_info(f"成功获取到返回值类型: {k}")
            return k

    print_info("使用默认的返回值类型: return-void")
    return "return-void"


def call_jar(jar_path, *args):
    # 构建命令行参数
    command = ['java', '-jar', jar_path] + list(args)

    # 调用子进程
    result = subprocess.run(command, capture_output=True, text=True)

    # 输出结果
    print("标准输出:", result.stdout)
    print("标准错误:", result.stderr)
    return result


def decompile(apk_path: str, output_path: str = ""):
    """
    反编译apk
    :param apk_path: apk路径
    :param output_path: 输出路径[可空]
    :return: 输出路径
    """
    # 若不指定输出路径则直接在apk位置输出
    if output_path == "":
        # 分割路径得到数组
        split: list = apk_path.split("/")
        # 删除最后一个元素得到路径
        apk_name = split.pop(-1)
        for s in split:
            output_path = os.path.join(output_path, s)
        # 最后合并apk名
        output_path = os.path.join(str(output_path), apk_name.split(".")[0])
        print_info(f"正在反编译 {apk_name} ...")

    if os.path.exists(output_path):
        print_warn("已经发现解压过的apk资源文件夹，rom可能已被修改过一次，正在删除原文件夹中...")
        shutil.rmtree(output_path)

    # 执行反编译操作
    call_jar(apktool, "-r", "-f", "d", apk_path, "-o", output_path)
    print_suc(f"成功! 已输出到{output_path}.")

    # 返回路径
    return output_path


def recompile(apk_datapath: str, output_path: str = ""):
    """
    回编译apk
    :param apk_datapath: 已经反编译的apk资源路径
    :param output_path: 输出apk路径【需要 xxx.apk】
    :return: 成功与否
    """
    if not os.path.exists(output_path):
        print_err("apk资源路径不存在！")
        return

    # 若不指定输出路径则直接输出数据路径名.apk
    if output_path == "":
        # 提取最后一个的文件夹名
        split = apk_datapath.split("/")
        apk_name = split.pop(-1)
        for s in split:
            output_path = os.path.join(output_path, s)
        # 最后再合成最终路径
        output_path = os.path.join(output_path, f"{apk_name}.apk")
        print_info(f"正在回编译 {apk_name}.apk ...")

    if not os.path.isdir(apk_datapath):
        print_err("无法找到对应的apk资源文件夹！")
        return False

    # 执行回编译操作
    call_jar(apktool, "b", apk_datapath, "-o", output_path)
    print_suc(f"成功! 已输出到{output_path}.")

    return True


def search(
        apk_datapath: str,
        content: str,
        style: str,
        search_path: str = None,
        regex_mode: bool = False,
        caps: bool = False,
        complete_match: bool = False,
) -> list:
    """
    搜索
    :param apk_datapath: apk解压资源路径
    :param content: 要搜索的内容
    :param style: 搜索类型【code-代码, class-类名, method-方法名, string-带冒号的字符串, int-整数】
    :param regex_mode: 正则表达式模式，默认关闭
    :param search_path: 指定搜索的路径【从apk_datapath开始作为根目录/】，默认为根目录
    :param caps: 区分大小写,默认不区分
    :param complete_match: 完全匹配，默认关闭，开启后搜索效率提高
    :return: 返回需要处理的smali列表
    """
    result_list = []
    count = 0

    # 若指定搜索路径,则使用合成路径
    if search_path is not None:
        p = os.path.join(str(apk_datapath), str(search_path))
    else:
        p = apk_datapath

    def search_method(ct: str):
        nonlocal count

        # 若完全匹配
        """
        在原始字符串r中，反斜杠 '\' 不会被视为转义字符，而是被视为普通字符
        在Windows系统中，文件路径通常使用反斜杠 '\' 分隔目录。使用原始字符串可以避免路径中的反斜杠被错误解析。
        """

        if not regex_mode:
            # 不使用正则表达式
            ct_list = ""
            for i in ct:
                ct_list += "["
                ct_list += i
                ct_list += "]"
            ct = ct_list

        # 获取相应的方法的正则表达式语法
        regex = method_regex(complete_match, ct)

        for root, dirs, files in os.walk(p):
            for f in files:
                # 首先得是smali文件
                if not f.endswith(".smali"):
                    continue

                file_path = os.path.join(root, f)
                with open(file_path, "r", encoding="utf-8") as ff:
                    for line in ff:
                        # 方法名一定是.method开头
                        if not line.startswith(".method"):
                            continue

                        # 若不区分大小写
                        if not caps:
                            result = re.search(regex, line, re.IGNORECASE)
                            if result:
                                result_list.append(file_path)
                                print_info(f"{count + 1}: {result}")
                                count += 1
                        else:
                            result = re.search(regex, line)
                            if result:
                                result_list.append(file_path)
                                print_info(f"{count + 1}: {result}")
                                count += 1
        return result_list

    def search_class(ct: str):
        nonlocal count
        nonlocal result_list

        """
        1. 得到目录
        2. 匹配对应目录是否有这个文件名.smali
        """

        all_files = []
        for root, dirs, files in os.walk(p):
            for f in files:
                all_files.append(os.path.join(root, f))

        # 是否完全匹配
        if complete_match:
            pattern = f"{ct}.smali"
        else:
            pattern = f"*{ct}*.smali"

        # 根据是否区分大小写开始搜索
        if not caps:
            result_list = [file for file in all_files if fnmatch.fnmatch(os.path.basename(file), pattern)]
        else:
            result_list = [file for file in all_files if fnmatch.fnmatchcase(os.path.basename(file), pattern)]

        # 打印结果
        for r in result_list:
            print_info(f"{count + 1}: {r}")

        # 长度即为搜索结果数
        count = len(result_list)

    def search_normal(ct: str, mode=""):
        nonlocal count
        print_info(f"正在查找内容 {ct}...")

        def content_modifier(ct2: str):
            nonlocal mode
            # 是否开启正则表达式
            if regex_mode:
                # 是否是字符串类型
                if mode == "string":
                    return "\"" + ct2 + "\""
                return ct2
            else:
                # 是否是字符串类型
                if mode == "string":
                    ct2 = "\"" + ct2 + "\""

                if not caps:
                    return ct2.lower()
                else:
                    return ct2

        # 开始逐个搜索
        for root, dirs, files in os.walk(p):
            for f in files:
                # 必须为smali类型的文件
                if not f.endswith(".smali"):
                    continue

                # 打开文件
                file_path = os.path.join(root, f)

                with open(file_path, "r", encoding="utf-8") as ff:
                    for line in ff:
                        line = content_modifier(line)
                        # 是否开启正则表达式
                        if regex_mode:

                            # 是否完全匹配
                            if complete_match:
                                # 是否区分大小写
                                if caps:
                                    result = re.match(content_modifier(ct), content_modifier(line))
                                else:
                                    result = re.match(content_modifier(ct), content_modifier(line), re.IGNORECASE)

                                if result:
                                    result_list.append(ff)
                                    count += 1
                            else:
                                if re.match(content_modifier(ct), content_modifier(line), re.IGNORECASE):
                                    result_list.append(ff)
                                    count += 1
                        else:

                            # 是否完全匹配
                            if complete_match:
                                if content_modifier(ct) == content_modifier(line):
                                    result_list.append(ff)
                                    count += 1
                            else:

                                if content_modifier(ct) in content_modifier(line):
                                    result_list.append(ff)
                                    count += 1

    if style == "code":
        search_normal(content)
    elif style == "string":
        search_normal(content, mode="string")
    elif style == "class":
        search_class(content)
    elif style == "method":
        search_method(content)
    else:
        print_err(f"未找到类型 {style}.")

    if count == 0:
        print_warn(f"查找{style_name[style]} '{content}' 无结果!\n")
    else:
        print_suc(f"查找{style_name[style]} '{content}' 完毕! 共找到 {count} 个结果.\n")

    return result_list


def search_in_smali(
        smali_files: list,
        content: str,
        caps: bool = False,
        regex_mode: bool = False,
        complete_match: bool = False,
        line_num_range=None
):
    """
    在 smali 中搜索内容
    :param line_num_range:
    :param smali_files: 传入的smali文件
    :param content: 搜索内容
    :param caps: 区分大小写，默认关闭
    :param regex_mode: 正则表达式，默认关闭
    :param complete_match: 完全匹配，默认关闭
    :param line_num_range: 行号区间【若有】，用于只在某个区间范围内搜索
    :return: 返回行号结果【字典】
    """

    result_line_dict: dict = {}
    # 保存搜索结果数
    count = 0
    # 保存当前行号
    line_num = 0

    # 空搜索结果
    if len(smali_files) == 0:
        return result_line_dict

    # 完全匹配和正则表达式冲突
    if complete_match and regex_mode:
        print_err("错误: 不能同时进行正则表达式和完全匹配操作!\n")
        return result_line_dict

    # 对搜索内容进行去大小写
    if not caps:
        content = content.lower()

    def get_result_in_line(line_content: str):
        nonlocal count
        nonlocal line_num

        line_num += 1

        # 保存原结果
        org_result = line_content

        # 是否区分大小写
        if not caps:
            line_content = line_content.lower()

        # 是否开启正则
        if regex_mode:
            # 是否区分大小写
            if not caps:
                s_r = re.search(f"{content}", line_content, re.IGNORECASE)
            else:
                s_r = re.search(f"{content}", line_content)
            if s_r:
                result_line_dict[f].append(line_num)
                print_info(f"{count + 1}: {org_result.strip()}")
                count += 1
        else:
            if content in line_content:
                result_line_dict[f].append(line_num)
                print_info(f"{count + 1}: {org_result.strip()}")
                count += 1

    for f in smali_files:
        with open(f, "r", encoding="utf-8") as ff:
            # 新建类名字典
            result_line_dict.update({str(f): []})

            if line_num_range is not None:
                lines = ff.readlines()
                for line in range(line_num_range[0], line_num_range[1]):
                    get_result_in_line(lines[line])
            else:
                for line in ff:
                    get_result_in_line(line)

    if count == 0:
        print_suc(f"查找代码 '{content}' 无结果!\n")
        return None
    else:
        print_suc(f"查找代码 '{content}' 完毕! 共找到 {count} 个结果.\n")

    return result_line_dict


def smali_compass(
        smali_files: list,
        method_name: str,
        operation: str,
        caps: bool = False,
        complete_match: bool = False,
        value: str = "",
):
    """
    指南针——对方法进行操作
    :param smali_files: 传入的smali文件
    :param method_name: 方法名
    :param operation: 操作
    :param caps: 是否区分大小写【默认开启，因为对方法的操作一般是精确的】
    :param complete_match: 是否完全匹配【默认开启，因为对方法的操作一般是精确的】
    :param value: 若需要传入一些值，则需要写此项【比如清空代码后面的0x?】


    rm_method 清空方法
    get_invoke 查找调用处
    get_override 查找重写方法
    cpy_method_sign 复制方法签名
    cpy_invoke_code 复制 invoke 代码

    :return:
    清空方法 —— 成功与否
    查找调用处 —— 返回smali_list和行号
    重写方法 —— 返回smali_list和行号
    复制方法签名 —— 返回str
    复制 invoke 代码 —— 返回str
    """

    def rm_method() -> bool:
        # 获取方法名的正则表达式语法
        regex = method_regex(complete_match, method_name)

        # 获取行号
        method_lines_dict = search_in_smali(
            smali_files,
            regex,
            caps,
            True,
            complete_match
        )

        # 首先要有搜索结果
        if method_lines_dict is None:
            print_err("指南针错误：没有搜索结果，无法定位到方法名.\n")
            return False

        # 依次对方法名进行删除代码处理
        for smali_file in smali_files:
            with open(smali_file, "r", encoding="utf-8") as ff, \
                    open(f"{smali_file}.tmp", "w", encoding="utf-8") as tmp:
                for k, v in method_lines_dict.items():
                    # 若文件名与字典key匹配,即搜索到的行号列表与文件名匹配
                    if k == smali_file:
                        # 则开始进行对目标行号进行处理
                        # 注意这里对 num 的修改不影响该层循环
                        for line_num in v:
                            # 首先要行号 -1, 目的是能够获得当前方法信息
                            line_num -= 1

                            # 读取原smali文件
                            lines = ff.readlines()

                            range_list = get_method_range_lines(lines, method_name, line_num)

                            # part1
                            r_t = get_register_type(lines[line_num + 1].strip())
                            lines[range_list[0]] = f"    .{r_t} 2" + "\n"
                            print_suc(f"将第 {range_list[0] + 1} 行修改为:    {r_t} 2")

                            # part2
                            m_t = get_method_type(lines[line_num].strip())

                            # 检查是否有传入value
                            if value == "" and m_t != "V":
                                print_err("错误: 清空方法时没有传入赋值参数！")
                                return False

                            set_value_dict = {
                                "Z": f"const/4 v0, 0x{value}",
                                "I": f"const/4 v0, 0x{value}",
                                "J": f"const-wide/16 v0, 0x{value}",
                                ";": f"const/4 v0, 0x{value}",
                                "V": "",
                            }
                            lines[range_list[0] + 1] = set_value_dict[m_t] + "\n"
                            print_suc(f"将第 {range_list[0] + 2} 行修改为:    {set_value_dict[m_t]}")

                            # part3
                            return_value_dict = {
                                "Z": f"return v0",
                                "I": f"return v0",
                                "J": f"return-wide v0",
                                ";": f"return-object v0",
                                "V": "return-void",
                            }
                            lines[range_list[0] + 2] = return_value_dict[m_t] + "\n"

                            print_suc(f"将第 {range_list[0] + 3} 行修改为:    {return_value_dict[m_t]}")

                            # 剩下的全删掉
                            range_list[0] = range_list[0] + 4
                            while range_list[0] < range_list[1] - 1:
                                lines[range_list[0]] = ""
                                range_list[0] += 1

                        tmp.writelines(lines)

                        get_line_num_belongs_method(lines, 668)

                        # 最后替换文件
                        # os.replace(f"{smali_file}.tmp", smali_file)
                        print_suc(f"成功清空了方法: {method_name}")
        return True

    def copy_method_signature(f: list) -> list:
        """
        复制方法签名
        :return: 返回整个调用方法的签名和apk_datapath位置【0位置签名，1位置apk_datapath】
        """
        """
        1.提取方法名以及右边部分
        2.加上箭头形成箭头函数
        """
        left = str(f[0]).replace("\\", "/").split("/")

        # 获取从smali下一个开始的索引值
        com_index = 0

        while not left[com_index].startswith("smali") and com_index < len(left) - 1:
            com_index += 1

        # 首处理
        com_index += 1
        left[com_index] = "L" + left[com_index]

        mixed_str = ""
        apk_datapath_str = ""
        result = []

        for i in range(com_index, len(left)):
            if i == len(left) - 1:
                mixed_str += left[i].replace(".smali", "") + ";"
            else:
                mixed_str += left[i] + "/"

        # 加上箭头
        mixed_str += "->"

        # 与方法名后半部分拼接
        regex = re.compile(f"<?\\w*{method_name}\\w*>?\\(.*\\)(Z|V|I|.*;)")

        with open(smali_files[0], "r", encoding="utf-8") as f:
            lines = f.readlines()
            for line in lines:
                regex_match = regex.search(line)
                if regex_match:
                    # 正则表达式需要转义

                    result.append(
                        mixed_str +
                        str(regex_match.group()
                            )
                    )
                    break

        for i in range(0, com_index - 1):
            apk_datapath_str += left[i] + "/"

        result.append(apk_datapath_str)
        return result

    def get_invoke() -> list:
        """
        查找调用处
        :return: 需要处理的smali列表
        """
        """
        思路：
        1. 获得方法签名
        3. 调用search方法
        4. 
        """

        # 获得方法签名
        sign_list: list = copy_method_signature(smali_files)

        print_info(f"成功获取到方法签名")

        result_list = search(
            sign_list[1],
            sign_list[0],
            "code",
        )

        return result_list

    if operation == "rm_method":
        rm_method()
    elif operation == "get_invoke":
        return get_invoke()


if __name__ == "__main__":
    method_name = "getOptimalDB"
    # 外搜索
    smalis = search(
        "OLD-QEUI/a/b/test",
        method_name,
        "method",
        regex_mode=False,
        caps=False,
        complete_match=False,
    )

    rl = smali_compass(

        smalis,
        method_name,
        "get_invoke",
    )

    for i in rl:
        print(i)