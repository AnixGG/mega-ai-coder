import json
import subprocess
from typing import Dict, Any
from langchain_core.tools import tool


@tool
def collect_docker_containers() -> Dict[str, Any]:
    """
    Collect information about running Docker containers.
    Returns a dictionary with container details including names, statuses, images, and ports.
    """
    try:
        result = subprocess.run(
            ["docker", "ps", "-a", "--format", "{{json .}}"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        
        if result.returncode != 0:
            return {
                "error": f"Failed to list containers: {result.stderr}",
                "containers": [],
            }
        
        containers = []
        for line in result.stdout.strip().split('\n'):
            if line:
                try:
                    container_info = json.loads(line)
                    containers.append(container_info)
                except json.JSONDecodeError:
                    continue
        
        return {
            "containers": containers,
            "count": len(containers)
        }
        
    except subprocess.TimeoutExpired:
        return {
            "error": "Command timed out while collecting Docker container information",
            "containers": [],
        }
    except FileNotFoundError:
        return {
            "error": "Docker is not installed or not in PATH",
            "containers": [],
        }
    except Exception as e:
        return {
            "error": f"An error occurred while collecting Docker container information: {str(e)}",
            "containers": [],
        }


@tool
def collect_docker_images() -> Dict[str, Any]:
    """
    Collect information about Docker images.
    Returns a dictionary with image details including repository, tag, ID, and size.
    """
    try:
        # Get list of all images
        result = subprocess.run(
            ["docker", "images", "--format", "{{json .}}"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        
        if result.returncode != 0:
            return {
                "error": f"Failed to list images: {result.stderr}",
                "images": [],
            }
        
        images = []
        for line in result.stdout.strip().split('\n'):
            if line:
                try:
                    image_info = json.loads(line)
                    images.append(image_info)
                except json.JSONDecodeError:
                    continue
        
        return {
            "images": images,
            "count": len(images),
        }
        
    except subprocess.TimeoutExpired:
        return {
            "error": "Command timed out while collecting Docker image information",
            "images": []
        }
    except FileNotFoundError:
        return {
            "error": "Docker is not installed or not in PATH",
            "images": []
        }
    except Exception as e:
        return {
            "error": f"An error occurred while collecting Docker image information: {str(e)}",
            "images": []
        }


@tool
def collect_docker_info() -> Dict[str, Any]:
    """
    Collect general Docker system information.
    Returns a dictionary with Docker version, system info, and resource usage.
    """
    try:
        # Get Docker version
        version_result = subprocess.run(
            ["docker", "--version"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        
        if version_result.returncode != 0:
            version = "Unknown"
        else:
            version = version_result.stdout.strip()
        
        # Get Docker system info
        info_result = subprocess.run(
            ["docker", "info", "--format", "{{json .}}"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        
        if info_result.returncode != 0:
            return {
                "error": f"Failed to get Docker info: {info_result.stderr}",
                "version": version,
                "info": {},
            }
        
        try:
            info_data = json.loads(info_result.stdout)
        except json.JSONDecodeError:
            info_data = {},
        
        return {
            "version": version,
            "info": info_data,
        }
        
    except subprocess.TimeoutExpired:
        return {
            "error": "Command timed out while collecting Docker information",
            "version": "Unknown",
            "info": {},
        }
    except FileNotFoundError:
        return {
            "error": "Docker is not installed or not in PATH",
            "version": "Unknown",
            "info": {},
        }
    except Exception as e:
        return {
            "error": f"An error occurred while collecting Docker information: {str(e)}",
            "version": "Unknown",
            "info": {},
        }