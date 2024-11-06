# 借助大模型实现精准测试未覆盖代码的接口测试用例补充设计
> 在实现精准测试后，团队中开始很多人抱怨精准测试并没有真是的帮助测试工程师提高质量。精准测试报告能够发现有些变更代码没又被测试用例覆盖到，但是要怎么覆盖就变成了一个难题。目前需要开发工程师和测试工程师一起讨论给出一些测试用例的补充，在精准测试覆盖率报告生成后需要让大家放下手工的工作一起来分析报告补充测试用例确实会有点不太好组织。

# 总体思路
从Jacoco的代码覆盖报告中可以知道哪行代码应该被覆盖却没有被覆盖。
![](https://s2.loli.net/2024/11/06/ywCqa8bg7uNjYUK.jpg)
就通过这个信息，借助大模型完成接口测试用例的补充分析，具体如下。
![](https://s2.loli.net/2024/11/06/UxfXlrJ6ChLy93s.jpg)

依据未覆盖的代码行，分析出所属代码行所在的函数，那么将未覆盖的行，函数信息一起给到大模型，让大模型给出能够覆盖这一行代码的单元测试用例。

在通过未覆盖代码及其所在函数，分析出调用该函数对外提供的api。然后再将被测试代码工程打包成一个文件，在和大模型反馈的单元测试用例组成一个新的prompt，再问大模型让它给出是否可以根据这个接口设计测试用例从而可以实现对应单元测试入参的输入，达到未覆盖代码行覆盖的目的。




## 通过未覆盖代码找到对应的函数和API

下面的代码就是通过项目的一行代码找到这行代码属于的函数，以及这行代码调用所涉及的API，代码中用到了一个开源的项目static_chain_analysis，用来分析变动代码和API的关系。
## 压缩代码
将本地代码打包成一个描述性文件，这里面包含了代码结构、代码详情，这样方便将整个项目直接上传到LLM，参考了https://github.com/Doriandarko/RepoToTextForLLM


## 大模型生成单元测试用例和接口测试分析
### 单元测试生成部分的prompt

```
You are a senior software test enginner.
You are goot at unit test case design methods such as line coverage, condition coverage, branch coverage, 
condition/branch coverage. 
please step by step thinking and  don't give feedback the each reasoning.
Uncover code by testcase is line {uncover_line_number}:{uncover_line_code}.
Dsign the function values for cover the uncover line code.
only have one line json,don't include other message.
{java_source_code}
```

### 接口测试分析的prompt
> 最近越来越体会到了提示词的各种框架、模板都是一个习惯，我们其实不必纠结。
```
<context>
    You are a senior software test enginner.
    You are goot at unit test case design methods such as line coverage, condition coverage, branch coverage, 
    condition/branch coverage. 
    please step by step thinking and  don't give feedback the each reasoning.
</context>
<objective>
Uncover code by testcase is line {uncover_line_number}:{uncover_line_code}.
</objective>
<target>
Dsign the function values for cover the uncover line code.
If the uncover line can't be covered by function params,please response message like {"status":"can not cover"}. 
</target>
<source>
{java_source}
</source>
<response>
only have one line json,don't include other message.
</response>
```
### QWen模型云服务的接口实现单测和接口分析功能


## 实现结果

![](https://s2.loli.net/2024/11/06/cmERbQoZqGD93u2.jpg)
最终的结果就是这样，大模型最终的结果有可能并不一定是告诉你输入那个测试用例就可以覆盖了，他会给出一段文字告诉我们应该输入什么，在什么其他依赖数据是什么条件下就可以达到测试覆盖的效果。