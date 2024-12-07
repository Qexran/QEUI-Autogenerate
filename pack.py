import os


# 运行win32程序/脚本
def run_win_program(tool, args):
    os.system(f"bin\\win32_program\\{tool} {args}")


# 打包img
def re_img(work_path: str, need_repack_list: list) -> bool:
    # 依次打包成img
    for i in need_repack_list:
        # 更新分区大小
        update_partition_size(work_path, i)
        # 获取分区大小
        size = get_partition_size(work_path, i)

        # 工作环境目录/分区目录
        mixed = f"{work_path}/{i}"

        # 正片开始
        run_win_program("make_ext4fs.exe",
                        "-l %s -T 0 -L %s/config/%s_file_contexts -C %s/config/%s_fs_config -a %s -s %s %s/%s"
                        % (
                            ###########################
                            # -l代表镜像输出大小
                            size,  # 打包镜像大小
                            ###########################
                            mixed,  # _file_contexts文件位置
                            i,  # 分区名_file_contexts
                            ###########################
                            mixed,  # _fs_config文件位置
                            i,  # 分区名_fs_config
                            ###########################
                            # -s 代表打包成 sparse 格式的镜像
                            i,  # 要打包的镜像标识名[严格的],通常与分区表匹配
                            f"{work_path}/{i}/qe_{i}.img",  # 要打包的镜像的名称[普通的],叫什么都可以
                            ###########################
                            mixed,  # 需要处理的镜像位置
                            i  # 需要处理的镜像位置
                            ###########################

                        )
                        )

    # 判断是否打包成功
    print(f"- 需要打包的分区:{need_repack_list}")
    for i in need_repack_list:
        if not os.path.exists(f"{work_path}/{i}.img"):
            print(f"- 打包 {i} 失败!")
            return False

    print(f"- 打包 {need_repack_list} 成功!")
    return True


# 通过config获取文件大小
def get_partition_size(work_path,partition_name) -> int:
    with open(f"{work_path}/{partition_name}/config/product_size.txt", "r", encoding="UTF-8") as f:
        return int(f.read())


# 修改过后分区大小需要更新到config
def update_partition_size(work_path, partition_name):
    # 定义总大小
    total_size: int = 0
    # 使用 os.walk 遍历指定路径下的所有子目录和文件
    for path, dirs, files in os.walk(f"{work_path}/{partition_name}/{partition_name}"):
        # 在遍历到的文件中
        for f in files:
            # 利用 os.path.join 来构建完整的文件路径【path,f 是路径+文件名】
            file_path = os.path.join(path, f)
            total_size += os.path.getsize(file_path)

    # 将 total_size 写入到config中
    with open(f"{work_path}/{partition_name}/{partition_name}_size.txt", "w", encoding="UTF-8") as f:
        f.write(str(total_size))


