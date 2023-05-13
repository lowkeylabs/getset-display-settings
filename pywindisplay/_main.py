''' pymonitor - CLI for manipulating windows display settings
'''
from loguru import logger
import click
import ctypes
import win32api
import win32con
import winerror
import pywintypes

# Constants for the SetDisplayConfig function
SDC_TOPOLOGY_INTERNAL = 0x00000001
SDC_TOPOLOGY_CLONE = 0x00000002
SDC_TOPOLOGY_EXTEND = 0x00000004
SDC_TOPOLOGY_EXTERNAL = 0x00000008
SDC_TOPOLOGY_SUPPLIED = 0x00000010

QDC_ALL_PATHS         = 0x00000001
QDC_ONLY_ACTIVE_PATHS = 0x00000002
QDC_DATABASE_CURRENT  = 0x00000004
QDC_INCLUDE_HMD = 0x00000020

class DISPLAYCONFIG_PATH_INFO(ctypes.Structure):
    _fields_ = [
        ('sourceInfo', ctypes.c_uint64),
        ('targetInfo', ctypes.c_uint64),
        ('flags', ctypes.c_uint32),
        ('sourceModeInfo', ctypes.c_uint64),
        ('targetModeInfo', ctypes.c_uint64),
        ('desktopImageInfo', ctypes.c_uint64)
    ]

class DISPLAYCONFIG_MODE_INFO(ctypes.Structure):
    _fields_ = [
        ('infoType', ctypes.c_uint32),
        ('id', ctypes.c_uint32),
        ('adapterId', ctypes.c_uint64),
        ('adapterIdLow', ctypes.c_uint32),
        ('targetId', ctypes.c_uint32),
        ('flags', ctypes.c_uint32),
        ('modeInfo', ctypes.c_uint64)
    ]

class DISPLAYCONFIG_SOURCE_MODE(ctypes.Structure):
    _fields_ = [
        ('width', ctypes.c_uint32),
        ('height', ctypes.c_uint32),
        ('pixelFormat', ctypes.c_uint32),
        ('position', ctypes.c_uint32),
    ]

class DISPLAYCONFIG_TARGET_MODE(ctypes.Structure):
    _fields_ = [
        ('targetVideoSignalInfo', ctypes.c_uint64),
        ('targetMode', DISPLAYCONFIG_SOURCE_MODE),
        ('rotation', ctypes.c_uint32),
        ('scaling', ctypes.c_uint32),
        ('refreshRate', ctypes.c_uint32),
        ('scanLineOrdering', ctypes.c_uint32),
    ]

class DISPLAYCONFIG_DEVICE_INFO_HEADER(ctypes.Structure):
    _fields_ = [
        ('type', ctypes.c_uint32),
        ('size', ctypes.c_uint32),
        ('adapterId', ctypes.c_uint64),
        ('id', ctypes.c_uint32)
    ]

class DISPLAYCONFIG_TARGET_DEVICE_NAME_FLAGS(ctypes.Structure):
    _fields_ = [
        ('value', ctypes.c_uint32)
    ]

# Function prototypes for SetDisplayConfig and QueryDisplayConfig
SetDisplayConfig = ctypes.windll.user32.SetDisplayConfig
SetDisplayConfig.argtypes = [
    ctypes.c_uint32, # numPathArrayElements
    ctypes.POINTER(DISPLAYCONFIG_PATH_INFO), # pathArray
    ctypes.c_uint32, # numModeInfoArrayElements
    ctypes.POINTER(DISPLAYCONFIG_MODE_INFO), # modeInfoArray
    ctypes.c_uint32 # flags
]

QueryDisplayConfig = ctypes.windll.user32.QueryDisplayConfig
QueryDisplayConfig.argtypes = [
    ctypes.c_uint32, # flags
    ctypes.POINTER(ctypes.c_uint32), # numPathArrayElements
    ctypes.POINTER(DISPLAYCONFIG_PATH_INFO), # pathArray
    ctypes.POINTER(ctypes.c_uint32), # numModeInfoArrayElements
    ctypes.POINTER(DISPLAYCONFIG_MODE_INFO), # modeInfoArray
    ctypes.POINTER(ctypes.c_uint32) # currentTopologyId
]

def set_display_mode(width, height, refresh_rate):
    # Get the current display settings
    num_path_info = ctypes.c_uint32()
    num_mode_info = ctypes.c_uint32()
    current_topology_id = ctypes.c_uint32

    QueryDisplayConfig(
        SDC_TOPOLOGY_INTERNAL | SDC_TOPOLOGY_CLONE | SDC_TOPOLOGY_EXTEND | SDC_TOPOLOGY_SUPPLIED,
        ctypes.byref(num_path_info),
        None,
        ctypes.byref(num_mode_info),
        None,
        ctypes.byref(current_topology_id)
    )

def get_display_mode():
    # Get the current display settings
    logger.debug("get_display_mode")
    num_path_info = ctypes.c_uint32()
    num_mode_info = ctypes.c_uint32()
    current_topology_id = ctypes.c_uint32()

    path_info_array = (DISPLAYCONFIG_PATH_INFO * 100)()
    mode_info_array = (DISPLAYCONFIG_MODE_INFO * 100)()

    return_code = QueryDisplayConfig(
#        QDC_ONLY_ACTIVE_PATHS,
        SDC_TOPOLOGY_INTERNAL | SDC_TOPOLOGY_CLONE | SDC_TOPOLOGY_EXTEND | SDC_TOPOLOGY_SUPPLIED,
        ctypes.byref(num_path_info),
        None,
        ctypes.byref(num_mode_info),
        None,
        ctypes.byref(current_topology_id)
    )
    logger.debug(f"return code: {return_code}")
    error_name = win32api.FormatMessage( return_code )
    logger.debug(f"{error_name}")
    logger.debug(f"num_path_info.value: {num_path_info.value}")
    logger.debug(f"num_mode_info.value: {num_mode_info.value}")
    logger.debug(f"current_topology_id: {current_topology_id}")
    logger.debug(f"displayconfig_path_info: {DISPLAYCONFIG_PATH_INFO}")

    return

    # Allocate arrays for the path and mode info
    path_info_array = (DISPLAYCONFIG_PATH_INFO * num_path_info.value)()
    mode_info_array = (DISPLAYCONFIG_MODE_INFO * num_mode_info.value)()

    # Call QueryDisplayConfig again to get the path and mode info
    QueryDisplayConfig(
#        QDC_ONLY_ACTIVE_PATHS,
#        QDC_ALL_PATHS,
        QDC_DATABASE_CURRENT | QDC_INCLUDE_HMD,
        ctypes.byref(num_path_info),
        path_info_array,
        ctypes.byref(num_mode_info),
        mode_info_array,
        ctypes.byref(current_topology_id)
    )

    # Print the current display settings
    for i in range(num_path_info.value):
        path_info = path_info_array[i]
        source_mode_info = DISPLAYCONFIG_SOURCE_MODE.from_address(path_info.sourceModeInfo)
        target_mode_info = DISPLAYCONFIG_TARGET_MODE.from_address(path_info.targetModeInfo)
        print(f"Display {i} resolution: {source_mode_info.width}x{source_mode_info.height}, refresh rate: {target_mode_info.refreshRate}Hz")


@click.command
def cli():
    logger.info("starting")

    get_display_mode()


if __name__=="__main__":
    cli()
