import pack  # 与打包有关
import unpack  # 与解包有关
import boot_killer  # 与boot处理有关
import rom_getter  # 与获取信息有关
import file_killer  # 与文件处理有关
import qeui_features  # QEUI功能相关
from color_text import print_suc, print_err, print_info, print_warn  # 彩色字体

# 统一工作环境
workspace = "workspace"


# 清道夫
def clean_workdir(workdir):
    # 工作环境
    file_killer.clean_file_or_folder(workdir)
    # 备份文件夹
    file_killer.clean_backup()


######################
# 清理工作环境
clean_workdir(workspace)

# 获取rom包路径
rom_file = input("- 请丢入ROM包...\n- 支持MIUI11, 安卓10\n")
# 将地址转义得到正常路径
rom_file = rom_file.replace("\\", "/")

# 解压压缩文件
unpack.unzip_file(rom_file, workspace)

# 解包,返回需要处理的分区list
# 检查rom一共存在多少个需要操作的分区
operate_list = ["system", "vendor", "product", "system_ext", "mi_ext"]
need_unpack_list = unpack.check_rom_and_unpack(workspace, operate_list)

######################
# 获取ROM的基本信息

# 获取分区路径信息[第二参数为若要寻找内分区, 扫描的位置]
partitions_dict = rom_getter.get_rom_structure("workspace", "system")

# 获取prop文件
prop_files = rom_getter.get_prop_files(partitions_dict)

# 抓取prop信息
property_dict = rom_getter.catch_device_information(prop_files)

######################
# 精简app并制作对应精简块模块包

# 一般情况下系统apk在这些文件夹中
apk_dirs = ["app", "priv-app"]

# 执行清理备份操作
file_killer.delete_miui_apks(partitions_dict, apk_dirs)

# 清理 data-app
file_killer.data_app_cleaner(partitions_dict)

######################
# 基础文件修改



######################
# 对 boot 和 vbmeta 进行处理

# 解包boot得到ramdisk和split_img
# ramdisk, split_img = boot_killer.un_boot(workspace, "boot")

# 处理vbmeta
# need_unlock_vbmeta_list = ["vbmeta", "vbmeta_system", "vbmeta_vendor"]
# boot_killer.unlock_vbmeta(workspace, need_unlock_vbmeta_list)
