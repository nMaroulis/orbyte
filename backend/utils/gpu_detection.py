"""
Utility module for detecting and querying NVIDIA GPUs using NVML.
"""
import pynvml
from typing import List, Dict, Any, Optional
import logging

# Set up logging
logger = logging.getLogger(__name__)

def get_system_gpus() -> List[Dict[str, Any]]:
    """
    Get a list of all NVIDIA GPUs in the system with their details.
    
    Returns:
        List[Dict[str, Any]]: A list of dictionaries containing GPU information.
    """
    gpus = []
    
    try:
        # Initialize NVML
        pynvml.nvmlInit()
        
        # Get number of GPUs
        device_count = pynvml.nvmlDeviceGetCount()
        
        for i in range(device_count):
            try:
                handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                
                # Get basic GPU info
                name = pynvml.nvmlDeviceGetName(handle).decode('utf-8')
                uuid = pynvml.nvmlDeviceGetUUID(handle).decode('utf-8')
                
                # Get memory info
                mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                total_memory_gb = round(mem_info.total / (1024 ** 3), 2)
                
                # Get utilization rates
                util = pynvml.nvmlDeviceGetUtilizationRates(handle)
                
                # Get temperature
                try:
                    temp = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
                except pynvml.NVMLError:
                    temp = None
                
                # Get power usage
                try:
                    power_usage = pynvml.nvmlDeviceGetPowerUsage(handle) / 1000.0  # Convert to Watts
                    power_limit = pynvml.nvmlDeviceGetEnforcedPowerLimit(handle) / 1000.0  # Convert to Watts
                except pynvml.NVMLError:
                    power_usage = None
                    power_limit = None
                
                # Get driver version
                try:
                    driver_version = pynvml.nvmlSystemGetDriverVersion().decode('utf-8')
                except pynvml.NVMLError:
                    driver_version = "Unknown"
                
                gpu_info = {
                    'index': i,
                    'name': name,
                    'uuid': uuid,
                    'memory_total_gb': total_memory_gb,
                    'memory_used_gb': round(mem_info.used / (1024 ** 3), 2),
                    'memory_free_gb': round(mem_info.free / (1024 ** 3), 2),
                    'utilization_gpu': util.gpu,
                    'utilization_memory': util.memory,
                    'temperature_c': temp,
                    'power_usage_w': power_usage,
                    'power_limit_w': power_limit,
                    'driver_version': driver_version,
                    'status': 'available'  # Default status
                }
                
                gpus.append(gpu_info)
                
            except pynvml.NVMLError as e:
                logger.error(f"Error getting info for GPU {i}: {str(e)}")
                continue
        
    except pynvml.NVMLError as e:
        logger.error(f"NVML Error: {str(e)}")
        raise RuntimeError(f"Failed to initialize NVML: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error getting GPU info: {str(e)}")
        raise RuntimeError(f"Failed to get GPU information: {str(e)}")
    finally:
        # Always try to shut down NVML
        try:
            pynvml.nvmlShutdown()
        except:
            pass
    
    return gpus

def get_gpu_by_uuid(uuid: str) -> Optional[Dict[str, Any]]:
    """
    Get information about a specific GPU by its UUID.
    
    Args:
        uuid: The UUID of the GPU to find.
        
    Returns:
        Optional[Dict[str, Any]]: The GPU information if found, None otherwise.
    """
    try:
        gpus = get_system_gpus()
        for gpu in gpus:
            if gpu['uuid'] == uuid:
                return gpu
        return None
    except Exception as e:
        logger.error(f"Error getting GPU by UUID {uuid}: {str(e)}")
        return None
