from typing import Literal, List, Any
from langchain_core.tools import tool
from langgraph.types import Command
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict, Annotated
from langchain_core.prompts.chat import ChatPromptTemplate
from langgraph.graph import START, StateGraph, END
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, AIMessage
from src.prompt_library.prompt import system_prompt
from src.utils.llms import LLMModel
from src.toolkit.toolkits import *

class Router(TypedDict):
    next: Literal["information_node", "booking_node", "FINISH"]
    reasoning: str

class AgentState(TypedDict):
    messages: Annotated[list[Any], add_messages]
    id_number: int
    next: str
    query: str
    current_reasoning: str
    iteration_count: int

class DoctorAppointmentAgent:
    def __init__(self):
        llm_model = LLMModel()
        self.llm_model=llm_model.get_model()
    
    def supervisor_node(self, state: AgentState) -> Command[Literal['information_node', 'booking_node', '__end__']]:
        print("**************************below is my state right after entering****************************")
        print(state)
        
        # Track iterations to prevent infinite loops
        current_iteration = state.get('iteration_count', 0) + 1
        print(f"***************** ITERATION COUNT: {current_iteration} *****************")
        
        # Force finish after 5 iterations to prevent infinite loops
        if current_iteration >= 5:
            print("!!!! MAX ITERATIONS REACHED - FORCING FINISH !!!!")
            return Command(goto=END, update={'next': 'FINISH', 'iteration_count': current_iteration})
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"user's identification number is {state['id_number']}"},
        ] + state["messages"]
        
        print("***********************this is my message*****************************************")
        print(messages)
        
       
        query = ''
        if len(state['messages']) == 1:
            query = state['messages'][0].content
        
        print("************below is my query********************")    
        print(query)
        
        response = self.llm_model.with_structured_output(Router).invoke(messages)
        
        goto = response["next"]
        
        print("********************************this is my goto*************************")
        print(goto)
        
        print("********************************")
        print(response["reasoning"])
            
        if goto == "FINISH":
            goto = END
            
        print("**************************below is my state****************************")
        print(state)
        
        if query:
            return Command(goto=goto, update={'next': goto, 
                                            'query': query, 
                                            'current_reasoning': response["reasoning"],
                                            'iteration_count': current_iteration,
                                            'messages': [HumanMessage(content=f"user's identification number is {state['id_number']}")]
                            })
        return Command(goto=goto, update={'next': goto, 
                                        'current_reasoning': response["reasoning"],
                                        'iteration_count': current_iteration}
                    )

    def information_node(self, state: AgentState) -> Command[Literal['supervisor']]:
        print("*****************called information node************")
    
        # Enhanced system prompt with intelligent tool selection
        system_prompt = """You are a specialized agent to provide information about doctor availability and hospital FAQs.

**CRITICAL INSTRUCTIONS FOR TOOL SELECTION:**

1. **Analyze the query intelligently** before asking for more information:
   - If the user mentions a SPECIALIZATION (dentist, cardiologist, etc.) → use check_availability_by_specialization
   - If the user mentions a SPECIFIC DOCTOR NAME → use check_availability_by_doctor
   - Common specialization keywords: dentist, general dentist, cosmetic dentist, orthodontist, pediatric dentist, emergency dentist, oral surgeon, prosthodontist

2. **Date handling:**
   - If user says "tomorrow", calculate it as next day from 01-01-2024 = 02-01-2024
   - If user says "today", use 01-01-2024
   - Format dates as DD-MM-YYYY (e.g., 02-01-2024)

3. **Specialization mapping:**
   - "dentist" or "a dentist" → use specialization "general_dentist"
   - User doesn't need to specify exact specialization name

4. **ONLY ask for clarification if:**
   - User mentioned neither specialization nor doctor name
   - Date is completely missing or ambiguous

5. **DO NOT ask for:**
   - Specific doctor name when user asked about specialization
   - Specialization type when "dentist" is mentioned (assume general_dentist)

**Available tools:**
- check_availability_by_doctor: requires doctor_name and desired_date
- check_availability_by_specialization: requires specialization and desired_date

**Current year is 2024**. Always format dates properly before calling tools.
"""
        
        system_prompt = ChatPromptTemplate.from_messages(
                [
                    (
                        "system",
                        system_prompt
                    ),
                    (
                        "placeholder", 
                        "{messages}"
                    ),
                ]
            )
        
        information_agent = create_react_agent(model=self.llm_model,tools=[check_availability_by_doctor,check_availability_by_specialization] ,prompt=system_prompt)
        
        try:
            result = information_agent.invoke(state)
            response_content = result["messages"][-1].content
        except Exception as e:
            print(f"ERROR in information_node: {e}")
            response_content = "I apologize, but I encountered an error checking availability. Please try rephrasing your query with specific details like the doctor's name or specialization and the desired date."
        
        return Command(
            update={
                "messages": state["messages"] + [
                    AIMessage(content=response_content, name="information_node")
                ]
            },
            goto="supervisor",
        )

    def booking_node(self, state: AgentState) -> Command[Literal['supervisor']]:
        print("*****************called booking node************")
    
        system_prompt = "You are specialized agent to set, cancel or reschedule appointment based on the query. You have access to the tool.\n Make sure to ask user politely if you need any further information to execute the tool.\n For your information, Always consider current year is 2024."
        
        system_prompt = ChatPromptTemplate.from_messages(
                [
                    (
                        "system",
                        system_prompt
                    ),
                    (
                        "placeholder", 
                        "{messages}"
                    ),
                ]
            )
        booking_agent = create_react_agent(model=self.llm_model,tools=[set_appointment,cancel_appointment,reschedule_appointment],prompt=system_prompt)

        result = booking_agent.invoke(state)
        
        return Command(
            update={
                "messages": state["messages"] + [
                    AIMessage(content=result["messages"][-1].content, name="booking_node")
                    #HumanMessage(content=result["messages"][-1].content, name="booking_node")
                ]
            },
            goto="supervisor",
        )

    def workflow(self):
        self.graph = StateGraph(AgentState)
        self.graph.add_node("supervisor", self.supervisor_node)
        self.graph.add_node("information_node", self.information_node)
        self.graph.add_node("booking_node", self.booking_node)
        self.graph.add_edge(START, "supervisor")
        self.app = self.graph.compile()
        return self.app