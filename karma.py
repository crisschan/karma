import gradio as gr
import os
import shutil
from linetrace import LineTrace
from testcase_designer_qwen import TestcaseDesignerQwen
from localrepo2txt import LocalRepo2Txt

target_project="target_project"
temp_project="temp_project"

def copy_repo(workspace):
    if os.path.exists(target_project):
        shutil.rmtree(target_project)
    
    # 创建目标目录
    os.makedirs(target_project, exist_ok=True)

    # 遍历源目录中的所有文件
    for filename in os.listdir(workspace):
        print(filename)
        source_file = os.path.join(workspace, filename)
        destination_file = os.path.join(target_project, filename)
        
        # 复制文件
        if os.path.isfile(source_file):
            shutil.copy2(source_file, destination_file)
        # 复制文件夹
        elif os.path.isdir(source_file):
            shutil.copytree(source_file, destination_file)


def analysis(workspace,uncover_code_file,uncover_code_line):
    copy_repo(workspace)
    line_trace = LineTrace(target_project, temp_project,uncover_code_file,int(uncover_code_line))

    all_need_info =line_trace.need_api()
    print(all_need_info)
    related_function = all_need_info["method"]
    related_api = all_need_info["API"].split("|")[1]
    related_uncovercode = all_need_info["uncover_code"]
    related_uncover_codeline_number=all_need_info["uncover_codeline_number"]

    local_repo_2_txt = LocalRepo2Txt("target_project")
    repo_detal = local_repo_2_txt.get_repo_txt()
    testcase_designer_qwen = TestcaseDesignerQwen()
    uncover_code_file_detail = open(temp_project+'/'+uncover_code_file, 'r').read()
    project_code=open(repo_detal, 'r').read()


    ut_params = testcase_designer_qwen.ut_case_design(related_uncover_codeline_number,related_uncovercode,uncover_code_file_detail)
    testcase_designer_qwen.api_case_design(project_code,related_api,related_uncovercode,ut_params)
    res_message = "未覆盖代码行："+str(related_uncover_codeline_number)+"\n"+ \
        "未覆盖代码："+related_uncovercode+"\n"+ \
        "未覆盖代码文件："+uncover_code_file+"\n"+ \
        "未覆盖代码所在函数："+related_function+"\n"+ \
        "未覆盖代码所在函数测试参数："+str(ut_params)+"\n"+\
        "未覆盖代码所在API："+related_api+"\n"+ \
        "最终的分析结果："+str(testcase_designer_qwen.api_case_design(project_code,related_api,related_uncovercode,ut_params))
    return res_message



html_title = """
<div align="center">
  <h1>Karma</h1>
  <p>caffeine from coffee drupe.</p>
</div>
"""

with gr.Blocks() as karma:
    with gr.Row():
        gr.HTML(html_title)
    with gr.Row():
        with gr.Column(scale=8):
            workspace=gr.Textbox(label="repo的本地路径",value="/Users/crisschan/workspace/JSpace/Spring-Boot-Sample-Project")
            uncover_code_file=gr.Textbox(label="未覆盖代码文件路径",value="/src/main/java/com/demo/bankapp/service/concretions/WealthService.java")
        with gr.Column(scale=2):

            uncover_code_line=gr.Textbox(label="未覆盖的代码行",value="70")
            analysis_btn = gr.Button(value="分析")
    with gr.Row():
            result_txt = gr.Textbox(label="分析结果",value="")
    
    analysis_btn.click(fn=analysis,inputs=[workspace,uncover_code_file,uncover_code_line],outputs=result_txt)

karma.launch(server_name="127.0.0.1",inbrowser=True,quiet=True,share=False)
