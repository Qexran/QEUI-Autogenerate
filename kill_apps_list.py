kill_app_dict = {
    # 一定是垃圾
    "rubbish_app": [
        "Updater",  # 系统更新
        "jjhome",  # 老人桌面
        "PicoTts",  # TTS语音
        "SYSOPT",  # 未知,无副作用
        "SettingsIntelligence",  # 设置建议
        "SharedStorageBackup",  # adb备份,估计没人用这个
        "UserDictionaryProvider",  # 用户字典
        "PhotoTable",  # 图片展示
        "BookmarkProvider",  # 远古浏览器的书签保存器
        "Protips",  # 远古小部件提示
        "BasicDreams",  # 远古动态壁纸
        "WallpaperCropper",  # 谷歌壁纸备份1
        "WallpaperBackup",  # 谷歌壁纸备份2
        "wps_lite",  # WPS精简版
        "Browser",  # 浏览器
        "PocketBanReceiver",  # 便携接收器+高危
        "BluetoothExt",  # 远古应用
        "EasterEgg",  # 彩蛋
        "Xman",  # MIUI11标识
        "Yman",  # MIUI11标识
        "MtkBrowser",  # MTK自带浏览器
        "datastatusnotification",  # 谷歌自带数据状态通知
        "CNEService",  # 高通公司的一个所谓的“智能”3G / 4G Wi-Fi无缝互通应用
        "QAS_DVC_MSP_VZW",  # 未知 由小新大大提供
        "VZWAPNLib",  # 未知 由小新大大提供
        "DMService",  # 数据管理服务
        "ConnMO",  # 未知 由小新大大提供
        "DCMO",  # 未知 由小新大大提供
        "MyVerizonServices",  # 未知 由小新大大提供
        "SprintDM",  # 未知 由小新大大提供
        "SprintHM",  # 未知 由小新大大提供
        "NexusWallpapersStubPrebuilt2017",  # 未知 由小新大大提供
        "WallpapersBReel2017",  # 未知 由小新大大提供
        "EuiccSupportPixel",  # 未知 由小新大大提供
        "EuiccGoogle",  # 未知 由小新大大提供
        "WfcActivation",  # 未知 由小新大大提供
        "EasterEgg"  # 安卓彩蛋
    ],
    # 谷歌应用
    "google_app": [  # 谷歌全家桶
        "Velvet",  # Google
        "GoogleLocationHistory",  # 谷歌位置历史
        "PrintRecommendationService",  # 打印推荐
        "CalendarGoogle",  # 日历
        "Gmail",  # 邮箱
        "GoogleContactsSyncAdapter",  # 联系人同步
        "GoogleOne",  # 谷歌云服务
        "GooglePay",  # 谷歌支付
        "LatinImeGoogle",  # 谷歌键盘
        "Gboard",  # 谷歌键盘
        "Maps",  # 谷歌地图
        "SpeechServicesByGoogle",  # 谷歌语音服务
        "YouTube",  # 油管
        "Lens",  # 谷歌版扫一扫
        "AndroidAutoStub",
        "CarrierServices",  # 运营商服务
        "GoogleAssistant",  # 谷歌助理
        "GoogleRestore",  # 谷歌恢复
        "BackupRestoreConfirmation",  # 谷歌备份服务
        "Turbo",  # 设备健康服务
        "Wellbeing",  # 数字健康
        "facebook - installer",  # Facebook
        "facebook - services"  # Facebook
    ],

    # 驾车模式
    "drive": [
        "CarWith",  # 小米驾车1
        "MIUIDriveMode",  # 驾车模式1
        "MiDrive",  # 小米驾车3
        "digitalkey",  # 数字钥匙框架
        "RideModeAudio"  # 驾驶模式音频播放
    ],

    # 打印机
    "print": [
        "BuiltInPrintService",
        "PrintSpooler"  # PrintSpooler
    ],

    # 小米无用服务【也许有用】
    "miui": [
        "XiaoaiRecommendation",  # 小米推荐
        "PowerChecker",  #
        # "MiuiDaemon"  # 远古服务,收集用户信息,抓取错误日志,管理温控"
        "MiRcs",  #
        "BatteryInfoQuery",  #
        "CarrierDefaultApp",  #
        "CameraExtensionsProxy",  # 相机？
        "StatementService",  #
        "CameraTools #CameraTools",  #
        "XiaomiModemDebugService",  #
        "WfdService",  #
        "MIUIAccessibility",  # 小米无障碍1"
        "NetworkBoost",  # 小米网络助力
        "UpnpService",  # 小米盒子相关
        "SecurityOnetrackService",  # 小米信息跟踪
        "greenguard"  # 家庭保护
    ],

    # 妙享中心
    "mirror": [
        "MirrorSmartHubPrivate",  #
        "Mirror",  # MIUI+Beta版
        "MiConnectService"  # 互联通信服务(妙享中心)
    ],

    # 游戏
    "game": [
        "GameCenter",  # 游戏中心 [旧]
        "MiGameService",  # 游戏服务
        "MiGameCenterSDKService"  # SDK
    ],

    # 设备测试
    "test": [
        "FingerprintExtensionService",  #
        "XiaomiModemDebugService",  #
        "MiModemDebugService ",  #
        "EngineerMode",  #
        "CameraTest",  #
        "SensorTestTool",  #
        "ModemTestBox",  #
        "GFTest #指纹测试",  #
        "GFManager #指纹管理",  #
        "Cit #鲁班",  #
        "com.miui.qr",  #
        "BTProductionLineTool",  #
        "Traceur #系统跟踪"  # ",  #
    ],

    # 日志相关
    "log": [
        "GPSLogSave #GPSlog存储",  #
        "GnssDebugReport",  #
        "MIUIReporter #UI信息工具",  #
        "BugReport #服务与反馈",  #
        "CatchLog",  #
        "MIService",  #
        "SystemHelper #帮助开发者获取参数?",  #
        "Traceur #系统跟踪",  #
        "diaglogger",  #
        "MIService"  #
    ],

    # 广告相关
    "ad": [
        "mab",  #
        "MDMConfig",  #
        "MDMLSample",  #
        "AnalyticsCore",  #
        "MSA #MSA",  #
        "NewHome #信息中心 [旧]"  #
    ],

    # 小米支付
    "mi_pay": [
        "PaymentService",
        "Mipay"
    ],

    # 音乐与视频
    "music_video": [
        "Video",  # 小米视频
        "Music"  # 音乐
    ],

    # 快应用
    "quick": [
        "HybridAccessory",
        "HybridPlatform"
    ],

    # 小爱
    "xiao_ai": [
        "VoiceAssist",  # 小爱同学
        "VoiceTrigger",
        "AiAsstVision",  # 小爱翻译
        "MIUIAiasstService",
        "mi_aiasst_service",  # 小爱通话
    ],

    # 安全键盘
    "safe_kkeyboard": [
        "SecurityInputMethod"
    ],

    # vip服务
    "vip": [
        "MIUIVipService",
        "VipServiceNew",
        "VipAccount"
    ],

    # 搜索
    "search": [
        "MIUIQuickSearchBox",
        "QuickSearchBox",
        "AppIndexProvider"  # 搜索设置(已废弃)
    ],

    # usim
    "usim": [
        "Stk",
        "SimAppDialog"
    ],

    # fm收音机
    "fm": [
        "FM",
        "MiRadio",
        "FMRadio",
    ],

    # NFC
    "nfc": [
        "NQNfcNci",
        "NextPay",  # NextPay
        "SecureElement",
        "TSMClient",  # TSM
        "Tag",
    ],

    # mtk服务
    "mtk": [
        "LocationEM2",  # 对定位无影响
        "YGPS",  # 对定位无影响
        "slaservice",  # 无用
        # SmartRatSwitch",  #mtk专属+高危
        "MtkCapCtrl",  # mtk专属+高危
        # MtkGbaService",  #mtk专属+高危
        "BatteryWarning",  # mtk专属
        "btlogger",  # mtk专属
        "DebugLoggerUI",  # mtk专属
        "DuraSpeed",  # mtk专属
        "MtkEmergencyInfo",  # mtk专属
        "MtkWallpaperPicker",  # mtk专属
        "#MtkCarrierConfig",  # mtk专属+高危
        "AutoDialer",  # mtk专属
        "ATMWifiMeta",  # mtk专属+高危
        "ReceiverController",  # 测听筒质量？
        "LPPeService",  # MTK专属在现在的酒店服务中指金钥匙服务,就如同五星酒店中的贴身管家
        "DuraSpeed",  # 快霸
    ],

    # 高通服务
    "qualcoom": [
        "SSGTelemetryService",  # 安全服务
        "FingerprintExtensionService",
        "QualcommVoiceActivation",  # 语音
        "WAPPushManager",  # WAPP推送
        "ONS",
        "diaglogger",
        "CallLogBackup",
        "BlockedNumberProvider",
        "PacProcessor",
        "IWlanService",  # WLAN
        "DMRegService",  # 未知，翻译为DM注册服务
    ],

    #
    "internation_apps": [
        # 国外部分属于data-app的软件会默认到app/priv-app
        "Notes",  # 笔记国际版
        "MIUIScreenRecorder",  # 录音机
        "MIUICompass",  # 指南针
        "Scanner",  # 扫一扫
        "FileExplorerGlobal",  # 文件管理国际版
        "SystemAppUpdater",  # 系统应用更新器
        "CleanMaster",  # 垃圾清理国际版
        "Calculator",  # 计算器国际版
        # 国际版奇怪的APK
        "GameCenterGlobal",  # 游戏中心
        "MiPicks",  # 商店
        "MiDrop",  # 快传
        "InMipay",  # 国际支付
        "SetupWizard",  # 开机引导
        "Chrome"  # 浏览器
    ]
}
