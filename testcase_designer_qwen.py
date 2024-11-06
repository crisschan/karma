# from langchain_ollama.llms import OllamaLLM
from dotenv import load_dotenv, find_dotenv
# from openai import OpenAI
from langchain_community.llms import Tongyi
from langchain_core.prompts import PromptTemplate
from json_repair import repair_json
import os
import json

class TestcaseDesignerQwen(object):
    def __init__(self):
        _=load_dotenv(find_dotenv())
        DASHSCOPE_API_KEY=os.getenv("DASHSCOPE_API_KEY")
        self.llm = Tongyi(dashscope_api_key=DASHSCOPE_API_KEY,model_name="qwen-Max",temperature=0.1)
        
    def ut_case_design(self,uncover_line_number:str,uncover_line_code:str,java_source_code:str)->json:
        with open('ut_case_design_usr.prompt', 'r') as file:
            prompt_template= file.read()
        prompt= PromptTemplate(template = prompt_template,input_variables=["uncover_line_number","uncover_line_code","java_source_code"])
        chain = prompt|self.llm
        res = chain.invoke({"uncover_line_number":uncover_line_number,"uncover_line_code":uncover_line_code,"java_source_code":java_source_code})
        return repair_json(res)
    def api_case_design(self,project_zip_code:str,direct_api:str,uncover_line_code:str,ut_params:str)->str:
        with open('api_case_design_usr.prompt', 'r') as file:
            prompt_template= file.read()
        prompt= PromptTemplate(
            template=prompt_template,
            input_variables=["project_code","direct_api","uncover_line_code","ut_params"]
        )
        chain = prompt|self.llm
        res = chain.invoke({"project_code":project_zip_code,
                            "direct_api":direct_api,
                            "uncover_line_code":uncover_line_code,
                            "ut_params":ut_params})
        
        # return repair_json(res)
        # change return res 
        return res
if __name__ == '__main__':
    testcase_designer_qwen = TestcaseDesignerQwen()

    project_code=open('/Users/crisschan/workspace/PySpace/karma/target_project/repopack-output.txt', 'r').read()
    api_json = {'method': ' com/demo/bankapp/service/concretions/WealthService.makeWealthExchange(Long, String, BigDecimal, boolean)void', 'API': '[http]|/transaction/create'}

    direct_api = api_json["API"].split("|")[1]

    uncover_line_code = 'wealthMap.put(Constants.MAIN_CURRENCY, wealthMap.get(Constants.MAIN_CURRENCY).subtract(tryEquivalent));'
    ut_params_json = {"userId": 1, "currency": "USD", "amount": "5000.00", "isBuying": 1}
    ut_params = json.dumps(ut_params_json)

    print(testcase_designer_qwen.api_case_design(project_code,direct_api,uncover_line_code,ut_params))