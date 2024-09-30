from langchain.chains.llm import LLMChain
from langchain_core.prompts import PromptTemplate


def get_chain(llm, template: str, input_variables=None, verbose=True, output_key=""):
    return LLMChain(
        llm=llm,
        prompt=PromptTemplate(
            input_variables=input_variables, template=template, verbose=verbose
        ),
        output_key=output_key,
        verbose=verbose,
    )
