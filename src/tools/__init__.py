from src.tools.filesystem_tool import list_files
from src.tools.analysis_tool import get_file_structure, read_file
from src.tools.edit_tool import replace_code_block, create_file
from src.tools.test_tool import run_tests
from src.tools.end_tool import end_tool
from src.tools.docker_tool import collect_docker_containers, collect_docker_images, collect_docker_info

TOOLS = [
    list_files,
    get_file_structure,
    read_file,
    replace_code_block,
    create_file,
    run_tests,
    end_tool,
    collect_docker_containers,
    collect_docker_images,
    collect_docker_info,
]